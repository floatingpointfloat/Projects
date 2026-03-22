import random
import pygame
from pygame import Vector2
import math
from sys import exit

WIDTH, HEIGHT = 1000, 1000

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity_simulation")
clock = pygame.time.Clock()

# variables:
G = 5
start_mass = 1500

#glow and bloom
bloom_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

class Body:
    def __init__(self, pos, vel, mass, color):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.mass = mass
        self.radius = math.sqrt(self.mass / math.pi) / 3
        self.color = color
        self.trail = []
        self.acc = Vector2(0, 0)

    def apply_gravity(self, other):
        direction = other.pos - self.pos
        distance = direction.length()

        force_magnitude = (G * self.mass * other.mass) / distance**2 + 0.01
        force_direction = direction.normalize()

        if distance <= 3:
            return

        # F = m / a -- a = F / m
        force_acceleration = force_magnitude / self.mass

        if distance <= (self.radius + other.radius) / 2:
            bodies.append(
                Body(
                    (self.pos * self.mass + other.pos * other.mass) / (self.mass + other.mass),
                    (self.vel * self.mass + other.vel * other.mass) / (self.mass + other.mass),
                    (self.mass + other.mass),(random.randint(0, 255),random.randint(0, 255),random.randint(0, 255))))
            if self in bodies:
                bodies.remove(self)
            if other in bodies:
                bodies.remove(other)
        else:
            self.acc += force_acceleration * force_direction

    def update(self, dt):
        self.vel += self.acc * dt
        self.pos += self.vel * dt
        self.acc = Vector2(0, 0)

    def draw_trail(self, trail_surface, bloom_surface):
        if len(self.trail) > 200:
            self.trail.pop(0)
        self.trail.append(self.pos.copy())

        for i in range(1, len(self.trail)):
            position1 = self.trail[i - 1]
            position2 = self.trail[i]
            alpha = int(255 * (i / len(self.trail)))
            width = int(3 * (i / len(self.trail))) + 1
            color_with_alpha = (*self.color, alpha)
            
            pygame.draw.line(trail_surface, color_with_alpha, position1, position2, width)
            if alpha > 50:
                pygame.draw.line(bloom_surface, color_with_alpha, position1, position2, width)

# bodies:
bodies = []
bodies = [
    Body((400, 500), (0, 10), 5000, (255, 255, 255)),
    Body((600, 500), (0, -10), 5000, (255, 255, 255)),
]
# bodies = [Body((500,500), (0, 0), 20000, 50, "yellow")]

while True:
    dt = clock.tick(10) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bodies = [
                    Body((400, 500), (0, 10), 5000, (255, 255, 255)),
                    Body((600, 500), (0, -10), 5000, (255, 255, 255)),
                ]
                start_mass = 1500
            if event.key == pygame.K_UP:
                start_mass += 1000
            if event.key == pygame.K_DOWN and start_mass > 1000:
                start_mass -= 1000

        if event.type == pygame.MOUSEBUTTONDOWN:
            initial_pos = Vector2(event.pos)
            second_pos = initial_pos
            dragging = True

            while dragging:
                start_vel = (second_pos - initial_pos) / 4
                screen.fill((0, 0, 0))

                for body in bodies:
                    pygame.draw.circle(screen, body.color, body.pos, body.radius)

                for event in pygame.event.get():
                    if event.type == pygame.MOUSEMOTION:
                        second_pos = Vector2(event.pos)

                    if event.type == pygame.MOUSEBUTTONUP:
                        color = random.choice([1, 2, 3])
                        if color == 1:
                            bodies.append(Body(initial_pos,start_vel,start_mass,(min(int(random.randint(0, 255)*4), 255),random.randint(0, 255),random.randint(0, 255))))
                            
                        elif color == 2:
                           bodies.append(Body(initial_pos,start_vel,start_mass,(random.randint(0, 255),min(int(random.randint(0, 255)*4), 255),random.randint(0, 255))))

                        elif color == 3:
                            bodies.append(Body(initial_pos,start_vel,start_mass,(random.randint(0, 255),random.randint(0, 255),min(int(random.randint(0, 255)*4), 255))))
                        dragging = False

                pygame.draw.line(screen, (255, 255, 255), initial_pos, second_pos, 3)
                pygame.display.update()

    for body in bodies:
        for other in bodies:
            if body != other:
                body.apply_gravity(other)

    for body in bodies:
        body.update(dt)

    screen.fill((0, 0, 0))
    bloom_surface.fill((0, 0, 0, 0))
    trail_surface.fill((0, 0, 0, 0))
    
    for body in bodies:
        body.draw_trail(trail_surface, bloom_surface)
    
    bodies_to_remove = []
    for body in bodies:
        pygame.draw.circle(screen, (255, 255, 255), body.pos, body.radius * 0.6)
        pygame.draw.circle(screen, body.color, body.pos, body.radius)
    
        brightness = sum(body.color) / 3
        if brightness > 100:
            pygame.draw.circle(bloom_surface, body.color, body.pos, body.radius)

        if abs(body.pos.x) > WIDTH*2 or abs(body.pos.y) > HEIGHT*2:
            bodies_to_remove.append(body)
    for body in bodies_to_remove:
        bodies.remove(body)
    
    #glow and bloom
    #blur
    small_blur = pygame.transform.smoothscale(bloom_surface, (WIDTH // 6, HEIGHT // 6))
    blur = pygame.transform.smoothscale(small_blur, (WIDTH, HEIGHT))
    
    screen.blit(trail_surface, (0, 0))
    screen.blit(blur, (0, 0), special_flags=pygame.BLEND_ADD)

    pygame.display.update()