from sys import exit
import pygame
from pygame import Vector2
import random

pygame.init()
screen = pygame.display.set_mode((1000, 1000))
pygame.display.set_caption("Bouncing Ball Simulation")
clock = pygame.time.Clock()

#variables
boundary = pygame.draw.circle(screen, (255, 255, 255), (500, 500), 500)
G = Vector2(0, 1000)  # Gravitational constant for the simulation
spawning_mass = 10

class Ball:
    def __init__(self, position, velocity, radius, color, mass):
        self.position = Vector2(position)
        self.velocity = Vector2(velocity)
        self.acceleration = Vector2(0, 0)
        self.radius = radius
        self.color = color
        self.mass = mass

    def update(self):
        self.acceleration = G
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt

        center = Vector2(500, 500)
        distance_from_center = self.position - center
        dist = distance_from_center.length()
        normal = distance_from_center.normalize()

        if dist + self.radius >= 500 and self.velocity.dot(normal) > 0:
            self.velocity = self.velocity.reflect(normal) * 0.97  # Dampen the velocity to simulate energy loss
            self.position = center + normal * (500 - self.radius)

    def collision(self, other):
        distance = self.position - other.position
        if distance.length() < self.radius + other.radius:
            normal = distance.normalize()
            relative_velocity = self.velocity - other.velocity
            velocity_along_normal = relative_velocity.dot(normal)

            if velocity_along_normal > 0:
                return

            restitution = 0.9  # Coefficient of restitution (bounciness)
            impulse_scalar = -(1 + restitution) * velocity_along_normal
            impulse_scalar /= (1 / self.radius) + (1 / other.radius)

            impulse = impulse_scalar * normal
            self.velocity += impulse / self.radius
            other.velocity -= impulse / other.radius
            
            penetration = self.radius + other.radius - distance.length()
            self.position += normal * (
                penetration * (other.mass / (self.mass + other.mass))
            )
            other.position -= normal * (
                penetration * (self.mass / (self.mass + other.mass))
            )

obj = []
while True:
    dt = clock.tick(60) / 1000  # Time in seconds since last frame
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            print(len(obj))
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = Vector2(pygame.mouse.get_pos())
            obj.append(Ball(pos, (0,0), 10, (random.randint(10, 255), random.randint(10, 255), random.randint(10, 255)), spawning_mass))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                obj.clear()
        
    
    screen.fill((0, 0, 0))
    pygame.draw.circle(screen, (255, 255, 255), (500, 500), 500)
    for ball in obj:
        ball.update()
        pygame.draw.circle(screen, ball.color, (int(ball.position.x), int(ball.position.y)), ball.radius)
    
    for _ in range(3):
        for i in range(len(obj)):
            for j in range(i + 1, len(obj)):
                if obj[i].position.distance_to(obj[j].position) <= obj[i].radius + obj[j].radius:
                    obj[i].collision(obj[j])
        
    pygame.display.update()
    fps = clock.get_fps()
    pygame.display.set_caption(f"Bouncing Ball Simulation | Bodies: {len(obj)} | FPS: {round(fps, 1)}")
