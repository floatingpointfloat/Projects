import random
import pygame

WIDTH,HEIGHT = 800,600
G = 10
AVAIBLE_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (128, 0, 128)]
WALL_WIDTH = 20

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Touch the correct color!")
clock = pygame.time.Clock()

class ball:
    def __init__(self, x, y, radius, color, speed_y, speed_x):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed_y = speed_y
        self.speed_x = speed_x

    def update_position(self):
        self.y += self.speed_y

        if self.x <= WALL_WIDTH and self.speed_x < 0:
            self.speed_x *= -1
        elif self.x >= WIDTH - WALL_WIDTH and self.speed_x > 0:
            self.speed_x *= -1

        self.x += self.speed_x

        self.speed_y += G

    def inputs(self, input):
        if input == "SPACE":
            self.speed_y -= 10

start_color = random.choice(AVAIBLE_COLORS)
ball = ball(WIDTH // 2, HEIGHT // 2, 20, random.choice(start_color), 0, -5)

class left_walls:
    def __init__(self):
        self.size = HEIGHT
        self.positions= [0]
        self.min_size = 20
        self.colors = [start_color]
        self.cells = 1

    def reset(self, ball_color):
        self.size = HEIGHT / self.cells
        self.positions = []
        for i in range(self.cells):
            self.positions.append(i * self.size)

        while True:
            self.colors = []
            for i in range(self.cells):
                self.colors.append(random.choice(AVAIBLE_COLORS))
            if ball_color in self.colors:
                break