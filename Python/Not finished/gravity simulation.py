#my try at verlet integration for a numerically stable n-body simulation of gravitation
# quadtree and barnes hut
# world - camera separated -> zoom, moving, 1000000**2 world
# (relatively) stable gravitation (softening) and collision
# spawning and manipulation of objects
import pygame
import numpy as np
from sys import exit
from collections import deque
import math
import random
import time

#variables
WIDTH, HEIGHT = 700, 700
world_size = 1000000
accuracy = 0.5

#setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity sim")
clock = pygame.time.Clock()

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

    self.tree_drawing(h,renderer) #debug purposes, comment out if it works fine

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
    if self.mass == 0: #doesn't make sense to compute
      return

    if self.children is None:
      for other_index in self.body_indices: #mehrere körper pro zelle, bei kleinen zellen
        if other_index == body_index:
          continue
        offset = sim.positions[other_index] - pos
        dist_sq = np.dot(offset, offset) + EPS * EPS
        dist = np.sqrt(dist_sq)
        inv_dist3 = 1 / (dist_sq * dist)
        sim.accelerations[body_index] += (offset * sim.G * sim.masses[other_index] * inv_dist3)
      return

    offset = self.com - pos

    dist_sq = np.dot(offset, offset) + EPS * EPS
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
    self.dt = 1/240
    self.framecount = 0
    self.positions = np.empty((0,2), dtype=np.float64)
    self.old_positions = np.empty((0,2), dtype=np.float64)
    self.accelerations = np.empty((0,2), dtype=np.float64)
    self.velocities = np.empty((0,2), dtype=np.float64)
    self.masses = np.empty(0, dtype=np.float64)
    self.radii = np.empty(0, dtype=np.float64)
    self.trails = []

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
    self.trails.append(deque(maxlen=200))
  
  def body_reset(self):
    self.positions = np.empty((0,2), dtype=np.float64)
    self.old_positions = np.empty((0,2), dtype=np.float64)
    self.accelerations = np.empty((0,2), dtype=np.float64)
    self.velocities = np.empty((0,2), dtype=np.float64)
    self.masses = np.empty(0, dtype=np.float64)
    self.radii = np.empty(0, dtype=np.float64)
    self.trails = []

  def calculate_acceleration(self):
    self.accelerations[:] = 0 #prevent accumulating accelerations - obvious reasons
    tree = Quadtree()
    objects_len = len(self.positions)

    for i in range(objects_len):
      tree.insert(self,i)

    for i in range(objects_len):
      tree.compute_acceleration(self,i,accuracy)

  def update_positions(self): #velocity verlet integration
    self.positions += (self.velocities * self.dt + 0.5 * self.accelerations * self.dt**2)

  def update_velocities(self, old_accelerations): #new velocities
    self.velocities += (0.5 * (old_accelerations + self.accelerations) * self.dt)

  def solve_collision(self): #still not optimised
    objects_len = len(self.positions)
    checked = set() #keine duplikate

    tree = Quadtree()

    for i in range(objects_len):
      tree.insert(self,i)

    for i in range(objects_len):
      found = []
      r = self.radii[i]
      search_radius =r + np.max(self.radii)

      tree.root.collision_partners(
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
        checked.add(pair)

        offset = self.positions[j] - self.positions[i]
        dist_sq = np.dot(offset,offset)
        min_dist = self.radii[j] + self.radii[i]

        if dist_sq == 0: #exploding
          continue

        if dist_sq < min_dist**2: #overlap
          dist = np.sqrt(dist_sq)
          penetration = min_dist - dist
          normal = offset / dist
          total_mass = self.masses[i] + self.masses[j]

          correction_i = (normal * penetration * (self.masses[j] / total_mass))
          correction_j = (normal * penetration * (self.masses[i] / total_mass))

          self.positions[i] -= correction_i
          self.positions[j] += correction_j

  def update_trails(self):
    if self.framecount % 3 == 0: #save computing power, it doesn't ned a point every frame
      for i in range(len(self.positions)):
        self.trails[i].append(self.positions[i].copy())

  def presets(self,preset): #presets to choose from
    if preset == 1:
      self.body_reset()
      self.add_body((world_size/2, world_size/2 + 300), (-10, 0), 20000) 
      self.add_body((world_size/2, world_size/2 - 300), (10,0), 20000)
    elif preset == 2:
      self.body_reset()
      center = np.array([world_size/2,world_size/2])
      for _ in range(150):
        r = abs(random.gauss(80, 60))
        rotation = random.uniform(0, 2*np.pi)

        pos = center + np.array([np.cos(rotation),np.sin(rotation)]) * r
        vel = np.array([random.uniform(0,2),random.uniform(0,2)])
        mass = random.uniform(20,50)

        self.add_body(pos,vel,mass)
    elif preset == 3:
      self.body_reset()
      self.add_body((world_size/2,world_size/2 + 300),(-10,0),20000)
      self.add_body((world_size/2,world_size/2 - 300),(10,0),20000)
      self.presets(2)

  def physics_update(self):
    self.old_positions = self.positions.copy() #needed for velocity update later on
    old_accelerations = self.accelerations.copy()

    self.update_positions()
    self.calculate_acceleration()
    self.update_velocities(old_accelerations)

    for _ in range(10): #several solves for stability
      self.solve_collision()

    self.velocities = (self.positions - self.old_positions) / self.dt #correct for collision

    #self.update_trails() #eeeeexpensive, not needed at first
    self.framecount += 1

class Renderer():
  def __init__(self, screen):
    self.screen = screen
    self.camera_pos = np.array([world_size/2,world_size/2])
    self.zoom = 1
    self.spawning_mass = 1500
    self.dragging = False
    self.fps = 0

  def screen_to_world(self, screen_pos): #changing screen coordinates into world coordinates and taking zooming into account
    return ((np.array(screen_pos) - np.array([WIDTH/2, HEIGHT/2])) / self.zoom + self.camera_pos)

  def world_to_screen(self, world_pos): #world coordinates to screen coordinates
    return ((world_pos - self.camera_pos) * self.zoom + np.array([WIDTH/2, HEIGHT/2]))

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
        if event.key == pygame.K_1:
          sim.presets(1)
        if event.key == pygame.K_2:
          sim.presets(2)
        if event.key == pygame.K_3:
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

    pygame.draw.rect(self.screen, (255,255,255), (topleft[0],topleft[1],world_size*self.zoom,world_size*self.zoom), width=10)

  def draw_to_screen(self):
    self.screen.fill((0,0,0)) #screen reset

    self.draw_drag_arrow()
    #self.draw_trail(sim)
    self.draw_bodies(sim)
    self.draw_world_border()

    self.fps += 1
    print(f"frame: {self.fps}")

sim = Simulation()
sim.presets(1) #colab debug setup (no visual feedback) :(
sim.calculate_acceleration()
renderer = Renderer(screen)

if __name__ == '__main__':
  while True:
    renderer.input_handling(sim)
    for _ in range(4): #substeps (sim.dt has to be 4 times higher to compensate and enable true substepping)
      sim.physics_update()
    renderer.draw_to_screen()

    pygame.display.flip()
    clock.tick(60)