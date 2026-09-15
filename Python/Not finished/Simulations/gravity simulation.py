#my try at verlet integration for a numerically stable n-body simulation of gravitation
# quadtree and barnes hut
# world - camera separated -> zoom, moving
# (relatively) stable gravitation and collision
# spawning and manipulation of objects
import pygame
import numpy as np
from sys import exit
from collections import deque
import math
import random
import time
from numba import njit

#variables
WIDTH, HEIGHT = 700, 700
world_size = 5000
accuracy = 1.2

#setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity sim")
clock = pygame.time.Clock()

@njit(fastmath=True, cache=True)
def leaf_acceleration(
    positions,
    masses,
    body_indices,
    body_index,
    px,
    py,
    G,
    ax,
    ay
):
    EPS = 2.0

    for k in range(len(body_indices)):
        other_index = body_indices[k]

        if other_index == body_index:
            continue

        dx = positions[other_index, 0] - px
        dy = positions[other_index, 1] - py

        dist_sq = dx*dx + dy*dy + EPS*EPS

        inv_dist = 1.0 / math.sqrt(dist_sq)
        inv_dist3 = inv_dist * inv_dist * inv_dist

        factor = G * masses[other_index] * inv_dist3

        ax += dx * factor
        ay += dy * factor

    return ax, ay

class Quadnodes():
  def __init__(self, x, y, size):
    self.x = x
    self.y = y
    self.size = size
    self.MIN_SIZE = 8
    self.MAX_BODIES = 4

    self.children = None
    self.body_indices = []
    self.com = np.zeros(2, dtype=np.float64)
    self.mass = 0

  def tree_drawing(self, h, renderer): #not optimal, I know. This is supposed to be done by the Rendering Engine. Simply for debugging, isn't going to stay
    screen_pos = renderer.world_to_screen(np.array([self.x, self.y]))
    screen_size = h * renderer.zoom
    pygame.draw.rect(
        renderer.screen,
        (255,255,255),
        (screen_pos[0],screen_pos[1],screen_size,screen_size),
        width=1)
    pygame.draw.rect(
        renderer.screen,
        (255,255,255),
        (screen_pos[0] + screen_size,screen_pos[1],screen_size,screen_size),
        width=1)
    pygame.draw.rect(
        renderer.screen,
        (255,255,255),
        (screen_pos[0],screen_pos[1] + screen_size,screen_size,screen_size),
        width=1)
    pygame.draw.rect(
        renderer.screen,
        (255,255,255),
        (screen_pos[0] + screen_size,screen_pos[1] + screen_size,screen_size,screen_size),
        width=1)

  def node_contains_pos(self,pos):
    return (self.x <= pos[0] < self.x + self.size
            and self.y <= pos[1] < self.y + self.size)

  def subdivide(self):
    h = self.size / 2

    #self.tree_drawing(h,renderer) #debug purposes, comment out if it works fine

    self.children = [
        Quadnodes(self.x,self.y,h),
        Quadnodes(self.x+h,self.y,h),
        Quadnodes(self.x,self.y+h,h),
        Quadnodes(self.x+h,self.y+h,h)
    ]

  def insert_into_children(self,sim,body_index):
    for child in self.children:
      if child.insert(sim,body_index):
        return True
    return False

  def insert(self,sim,body_index):
    pos = sim.positions[body_index]
    mass = sim.masses[body_index]

    if not self.node_contains_pos(pos):
      return False

    new_mass = self.mass + mass
    if new_mass > 0: #stop division by 0
      self.com = (self.com * self.mass + pos * mass) / new_mass
    self.mass = new_mass

    if self.children is None:
      if self.size <= self.MIN_SIZE or len(self.body_indices) < self.MAX_BODIES:
        self.body_indices.append(body_index)
        return True #einfach an indices angehängt

      self.subdivide()
      old_body_indices = self.body_indices
      self.body_indices = []
      for old_body_index in old_body_indices:
        self.insert_into_children(sim,old_body_index)
      self.insert_into_children(sim,body_index)
      return True
    else:
      self.insert_into_children(sim,body_index)
      return True

  def compute_acceleration(self,sim,body_index,accuracy=0.5): #accuracy = theta, controls the threshhold of grouping
    EPS = 2
    pos = sim.positions[body_index]
    sim.nodevisits += 1
    if self.mass == 0: #doesn't make sense to compute
      return

    if self.children is None:
      #mehrere körper pro zelle, bei kleinen zellen
      px = pos[0]
      py = pos[1]
      
      ax = sim.accelerations[body_index, 0]
      ay = sim.accelerations[body_index, 1]
      
      body_indices = np.asarray(
          self.body_indices,
          dtype=np.int64
          )
      
      ax, ay = leaf_acceleration(sim.positions,sim.masses,body_indices,body_index,px,py,sim.G,ax,ay)
      sim.accelerations[body_index, 0] = ax
      sim.accelerations[body_index, 1] = ay
      return

    offset = self.com - pos

    dx = offset[0] #python effizienter
    dy = offset[1]
    dist_sq = dx*dx + dy*dy + EPS * EPS

    if dist_sq < 1e-12:
      return

    dist = np.sqrt(dist_sq)

    if (self.size / dist < accuracy): #barnes hut threshold makes grouping possible
        inv_dist3 = 1 / (dist_sq * dist)
        sim.accelerations[body_index] += (offset * sim.G * self.mass * inv_dist3)
    else:
      for child in self.children:
        if child.mass > 0: #only traverse the neccessary parts of the tree
          child.compute_acceleration(sim,body_index,accuracy)

  def intersects_node(self,x,y,size): #fir collisions - check, if a partner is in the same leaf node
    return not (self.x + self.size < x or
                self.x > x + size or
                self.y + self.size < y or
                self.y > y + size)

  def collision_partners(self, x, y, size, found):
    if not self.intersects_node(x, y, size):
      return

    if self.children is None:
      found.extend(self.body_indices)
      return

    for child in self.children:
      child.collision_partners(x, y, size, found)

class Quadtree(): #"wrapperclass"
  def __init__(self):
    self.root = Quadnodes(0,0, world_size) #i didn'g limit the size of the world to the screen

  def insert(self,sim,body_index):
    self.root.insert(sim,body_index)

  def compute_acceleration(self,sim,body_index,accuracy):
    self.root.compute_acceleration(sim,body_index,accuracy)

class Simulation():
  def __init__(self):
    self.G = 10
    self.dt = 1/120
    self.framecount = 0
    self.bodies_to_break = set() #can't break the same body twice
    self.positions = np.empty((0,2), dtype=np.float64)
    self.old_positions = np.empty((0,2), dtype=np.float64)
    self.accelerations = np.empty((0,2), dtype=np.float64)
    self.velocities = np.empty((0,2), dtype=np.float64)
    self.masses = np.empty(0, dtype=np.float64)
    self.radii = np.empty(0, dtype=np.float64)
    self.trails = []
    self.cooldowns = np.empty(0, dtype=np.float64)
    self.tree = Quadtree()
    self.nodevisits = 0

  def add_body(self, pos, vel, mass):
    pos = np.array(pos, dtype=np.float64)
    vel = np.array(vel, dtype=np.float64)
    mass = float(mass)

    self.positions = np.vstack([self.positions, pos])
    self.old_positions = np.vstack([self.old_positions, pos.copy()])
    self.velocities = np.vstack([self.velocities, vel])
    self.masses = np.append(self.masses, mass)
    self.radii = np.append(self.radii, (math.sqrt(mass / math.pi) / 6)) #radius in relation to mass, change the number at the end to change size
    self.accelerations = np.vstack([self.accelerations, np.zeros(2)])
    self.cooldowns = np.append(self.cooldowns,0)
    self.trails.append(deque(maxlen=200))

  def body_reset(self):
    self.positions = np.empty((0,2), dtype=np.float64)
    self.old_positions = np.empty((0,2), dtype=np.float64)
    self.accelerations = np.empty((0,2), dtype=np.float64)
    self.velocities = np.empty((0,2), dtype=np.float64)
    self.masses = np.empty(0, dtype=np.float64)
    self.radii = np.empty(0, dtype=np.float64)
    self.trails = []
    self.cooldowns = np.empty(0, dtype=np.float64)

  def calculate_acceleration(self): #this needs extremely much power to compute, tree needs to be fixed
    self.accelerations[:] = 0 #prevent accumulating accelerations - obvious reasons
    objects_len = len(self.positions)
    self.tree = Quadtree()

    for i in range(objects_len):
      self.tree.insert(self,i)

    for i in range(objects_len):
      self.tree.compute_acceleration(self,i,accuracy)

  def update_positions(self): #velocity verlet integration
    self.positions += (self.velocities * self.dt + 0.5 * self.accelerations * self.dt**2)

  def update_velocities(self, old_accelerations): #new velocities
    self.velocities += (0.5 * (old_accelerations + self.accelerations) * self.dt)

  def impact_breaking(self,body_index):
    impact_pos = self.positions[body_index].copy()
    fragment_count = random.randint(2,5)
    weights = np.random.uniform(0.5, 1.5, fragment_count) #maintain the original mass
    weights /= weights.sum()
    fragment_masses = weights * self.masses[body_index]
    for i in range(fragment_count):
      angle = (2*np.pi*i)/fragment_count #uniform distribution
      angle += random.uniform(-0.2,0.2)
      offset = np.array([
          np.cos(angle),
          np.sin(angle)])
      fragment_radius = math.sqrt(fragment_masses[i] / math.pi) / 6
      spawn_pos = (impact_pos + offset * (self.radii[body_index] + fragment_radius)) #spawning the bodies outside of the parent body
      spawn_vel = self.velocities[body_index] + np.array([random.uniform(-1,1),random.uniform(-1,1)])

      self.add_body(spawn_pos,spawn_vel,fragment_masses[i])
      self.cooldowns[-1] = 200

    #deleting the body
    self.positions = np.delete(self.positions,body_index,axis=0)
    self.old_positions = np.delete(self.old_positions,body_index,axis=0)
    self.velocities = np.delete(self.velocities,body_index,axis=0)
    self.accelerations = np.delete(self.accelerations,body_index,axis=0)
    self.masses = np.delete(self.masses,body_index,axis=0)
    self.radii = np.delete(self.radii,body_index,axis=0)
    del self.trails[body_index]
    self.cooldowns = np.delete(self.cooldowns,body_index,axis=0)

  def collision_velocity_correcting(self,i,mass_i,j,mass_j,normal):
    relative_velocity = self.velocities[j] - self.velocities[i]
    velocity_along_normal = np.dot(relative_velocity, normal)
    if velocity_along_normal > 0: #bodys are already moving apart
      return
    bounciness = 0.3 #1 = perfectly elastic, 0 = opposite
    impulse = -(1 + bounciness) * velocity_along_normal
    impulse /= (1 / mass_i + 1 / mass_j)
    impulse_vector = impulse * normal

    #velocity correcting
    self.velocities[i] -= impulse_vector / mass_i
    self.velocities[j] += impulse_vector / mass_j

  def solve_collision(self): #still not completely optimised
    objects_len = len(self.positions)
    checked = set() #keine duplikate
    max_radius = np.max(self.radii)

    for i in range(objects_len):
      found = []
      r = self.radii[i]
      search_radius = r + max_radius

      self.tree.root.collision_partners(
          self.positions[i][0] - search_radius,
          self.positions[i][1] - search_radius,
          search_radius * 2,
          found)

      for j in found:
        if i >= j:
          continue

        pair = (i,j)
        if pair in checked:
          continue

        offset = self.positions[j] - self.positions[i]

        dx = offset[0]
        dy = offset[1]
        dist_sq = dx*dx + dy*dy

        dist = np.sqrt(dist_sq)
        min_dist = self.radii[j] + self.radii[i]

        if dist_sq == 0: #prevent exploding
          continue

        checked.add(pair)

        if dist_sq < min_dist**2: #overlap
          normal = offset / dist
          relative_velocity = self.velocities[j] - self.velocities[i]
          relative_velocity_normal = np.dot(relative_velocity,normal)
          if relative_velocity_normal > 35:
            mass_difference = abs(self.masses[j] - self.masses[i])
            if mass_difference < 3000 and self.masses[i] >= 1000 and self.masses[j] >= 2000:
              if self.cooldowns[i] <= 0:
                self.bodies_to_break.add(i)
              if self.cooldowns[j] <= 0:
                self.bodies_to_break.add(j)
            elif mass_difference >= 3000:
              if self.masses[j] < self.masses[i] and self.cooldowns[j] <= 0 and self.masses[j] >= 2000:
                self.bodies_to_break.add(j)
              elif self.cooldowns[i] <= 0 and self.masses[i] >= 2000:
                self.bodies_to_break.add(i)

          penetration = min_dist - dist
          mass_i = self.masses[i].copy()
          mass_j = self.masses[j].copy()
          total_mass = mass_i + mass_j

          correction_i = (normal * penetration * (mass_j / total_mass))
          correction_j = (normal * penetration * (mass_i / total_mass))

          self.positions[i] -= correction_i
          self.positions[j] += correction_j

          #velocity correcting
          self.collision_velocity_correcting(i,mass_i,j,mass_j,normal)

  def check_block_breaking(self):
    for index in sorted(set(self.bodies_to_break), reverse=True):
      self.impact_breaking(index)
    self.bodies_to_break.clear()

  def update_trails(self):
    if self.framecount % 3 == 0: #save computing power, it doesn't ned a point every frame
      for i in range(len(self.positions)):
        self.trails[i].append(self.positions[i].copy())

  def presets(self,preset): #presets to choose from
    if preset == 1:
      self.body_reset()
      self.add_body((world_size/2, world_size/2 + 300), (0,-20), 20000)
      self.add_body((world_size/2, world_size/2 - 300), (0,20), 20000)
    elif preset == 2:
      self.body_reset()
      center = np.array([world_size/2,world_size/2])
      for _ in range(25):
        r = abs(random.gauss(80, 60))
        rotation = random.uniform(0, 2*np.pi)

        pos = center + np.array([np.cos(rotation),np.sin(rotation)]) * r
        vel = np.array([random.uniform(0,2),random.uniform(0,2)])
        mass = random.uniform(20,50)

        self.add_body(pos,vel,mass)
    elif preset == 3:
      self.presets(2)
      self.add_body((world_size/2,world_size/2 + 300),(-10,0),20000)
      self.add_body((world_size/2,world_size/2 - 300),(10,0),20000)
    elif preset == 4:
      for i in range(int(WIDTH/20)):
        for j in range(int(HEIGHT/20)):
          sim.add_body((30*i,30*j),(0,0),100)

  def physics_update(self):
    self.nodevisits = 0
    self.old_positions = self.positions.copy() #needed for velocity update later on
    old_accelerations = self.accelerations.copy()

    self.update_positions()

    start = time.perf_counter()
    self.calculate_acceleration()
    print("acceleration: ",(time.perf_counter() - start)*1000,"ms")

    self.update_velocities(old_accelerations)

    start = time.perf_counter()
    for _ in range(4): #several solves for stability
      self.solve_collision()
    self.check_block_breaking()
    print("collision: ", (time.perf_counter() - start) * 1000, "ms")

    print(self.nodevisits)

    #self.update_trails() #eeeeexpensive, not needed at first
    self.framecount += 1
    self.cooldowns[:] -= 1

class Renderer():
  def __init__(self, screen):
    self.screen = screen
    self.camera_pos = np.array([world_size/2,world_size/2])
    self.zoom = 1
    self.spawning_mass = 1500
    self.dragging = False
    self.font = pygame.font.SysFont("Arial",15)

  def screen_to_world(self, screen_pos):
    return(
        (screen_pos[0] - WIDTH * 0.5) / self.zoom + self.camera_pos[0],
        (screen_pos[1] - HEIGHT * 0.5) / self.zoom + self.camera_pos[1]
    )

  def world_to_screen(self, world_pos):
    return (
        (world_pos[0] - self.camera_pos[0]) * self.zoom + WIDTH * 0.5,
        (world_pos[1] - self.camera_pos[1]) * self.zoom + HEIGHT * 0.5
    )

  def camera_reset(self):
    self.zoom = 1
    self.camera_pos = np.array([world_size/2,world_size/2])

  def constant_key_detection(self): #for continous key events
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and self.spawning_mass < 20000:
      self.spawning_mass += 5
    if keys[pygame.K_DOWN] and self.spawning_mass > 50:
      self.spawning_mass -= 5
    if keys[pygame.K_w] and self.camera_pos[1] >= 0: #prevent moving beyond the edges
      self.camera_pos[1] -= 4 / self.zoom
    if keys[pygame.K_s] and self.camera_pos[1] <= world_size - HEIGHT:
      self.camera_pos[1] += 4 / self.zoom
    if keys[pygame.K_a] and self.camera_pos[0] >= 0:
      self.camera_pos[0] -= 4 / self.zoom
    if keys[pygame.K_d] and self.camera_pos[0] <= world_size - WIDTH:
      self.camera_pos[0] += 4 / self.zoom

  def input_handling(self,sim):
    self.constant_key_detection()
    for event in pygame.event.get(): #single presses
      if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
        pygame.quit()
        exit()
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
        sim.add_body(self.screen_to_world(event.pos), (0,0), self.spawning_mass)
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #drag body append
        self.dragging = True
        self.drag_start = self.screen_to_world(event.pos)
      if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        self.dragging = False
        self.drag_end = self.screen_to_world(event.pos)
        vel = (np.array(self.drag_end) - np.array(self.drag_start)) * 0.1
        sim.add_body(self.drag_start,vel,self.spawning_mass)
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_0:
          self.camera_reset()
          sim.body_reset()
        if event.key == pygame.K_1:
          self.camera_reset()
          sim.presets(1)
        if event.key == pygame.K_2:
          self.camera_reset()
          sim.presets(2)
        if event.key == pygame.K_3:
          self.camera_reset()
          sim.presets(3)
      if event.type == pygame.MOUSEWHEEL: #zoom
        if event.y < 0 and self.zoom > 0.1:
          self.zoom *= 0.9
        elif event.y > 0 and self.zoom < 10:
          self.zoom *= 1.1

  def draw_bodies(self,sim):
    for i in range(len(sim.positions)):
      pos = self.world_to_screen(sim.positions[i])
      pygame.draw.circle(
          self.screen,
          (130, 90, int(min(255, 60 + 4 * np.linalg.norm(sim.velocities[i])))), #adjust color for speed
          pos,
          int(sim.radii[i]*self.zoom))

  def draw_drag_arrow(self):
    if self.dragging:
      pygame.draw.line(self.screen, (255,255,255), self.world_to_screen(self.drag_start), pygame.mouse.get_pos(), 2)

  def draw_trail(self,sim): #trail color still needs to optimised
      for i in range(len(sim.trails)):
        points = []
        for point in sim.trails[i]:
          points.append(self.world_to_screen(point))
        if len(sim.trails[i]) > 1:
          pygame.draw.lines(self.screen, (130, 90, int(min(255, 60 + 4 * np.linalg.norm(sim.velocities[i])))), False, points, 2)

  def draw_world_border(self):
    topleft = self.world_to_screen((0,0))

    pygame.draw.rect(self.screen,
        (255,255,255),
        (topleft[0],topleft[1],world_size*self.zoom,world_size*self.zoom),
        width=10)

  def show_fps(self):
    fps = round(clock.get_fps(),1)
    print(f"FPS: {fps}") #debug colab, remove later

    fps_surf = self.font.render(f"FPS: {fps}",True,(255, 255, 255))
    self.screen.blit(fps_surf, (10,10))

  def show_amount_of_bodies(self,sim):
    amount_of_bodies = len(sim.positions)
    amount_surf = self.font.render(f"Bodies: {amount_of_bodies}",True,(255,255,255))
    self.screen.blit(amount_surf,(10,40))
    print(f"Bodies: {amount_of_bodies}") #colab debug, remove later

  def show_zoom(self):
    zoom_surf = self.font.render(f"Zoom: {self.zoom}",True,(255,255,255))
    self.screen.blit(zoom_surf,(10,70))

  def show_technical_info(self):
    self.show_fps()
    self.show_amount_of_bodies(sim)
    self.show_zoom()

  def draw_to_screen(self):
    self.screen.fill((0,0,0)) #screen reset

    self.draw_drag_arrow()
    #self.draw_trail(sim)
    self.draw_bodies(sim)
    self.draw_world_border()

    self.show_technical_info()

sim = Simulation()
sim.presets(1) #colab debug setup (no visual feedback) :(
sim.calculate_acceleration()
renderer = Renderer(screen)

if __name__ == '__main__':
  while True:
    renderer.input_handling(sim)
    for _ in range(2): #substeps (sim.dt has to be 4 times higher to compensate and enable true substepping)
      sim.physics_update()
    renderer.draw_to_screen()

    pygame.display.flip()
    clock.tick(120)