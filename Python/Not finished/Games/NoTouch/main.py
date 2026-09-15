import random
import pygame
from sys import exit

WIDTH,HEIGHT = 800,600
G = 3
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
        self.G = G

    def update_position(self, dt):
        self.y += self.speed_y * dt

        self.x += self.speed_x * dt

        self.speed_y += self.G * dt

    def inputs(self, input):
        if input == "SPACE":
            self.speed_y = -20

start_color = random.choice(AVAIBLE_COLORS)
ball = ball(WIDTH // 2, HEIGHT // 2, 5, start_color, 0, -20)

class left_wall:
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

    def collision(self, ball):
        for i in range(self.cells):
            if self.positions[i] <= ball.y <= self.positions[i] + self.size:
                if self.colors[i] == ball.color:
                    return False
                else:
                    return True

class right_wall:
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

    def collision(self, ball):
        for i in range(self.cells):
            if self.positions[i] <= ball.y <= self.positions[i] + self.size:
                if self.colors[i] == ball.color:
                    return False
                else:
                    return True

left_wall = left_wall()
right_wall = right_wall()

class simulation:
    def __init__(self):
        self.left_wall = left_wall
        self.right_wall = right_wall
        self.ball = ball
        self.score = 0
        self.game_over = False
        self.G = G
        self.dt = 1 / 60

    def update(self):
        self.ball.update_position(self.dt)

        if self.ball.x - self.ball.radius <= WALL_WIDTH:
            if self.left_wall.collision(self.ball):
                self.game_over = True
            else:
                self.score += 1
                if self.right_wall.cells <= 20:
                    self.right_wall.cells += 1
                self.ball.color = random.choice(AVAIBLE_COLORS)
                self.right_wall.reset(self.ball.color)
                self.ball.speed_x *= -1
        if self.ball.x + self.ball.radius >= WIDTH - WALL_WIDTH:
            if self.right_wall.collision(self.ball):
                self.game_over = True
            else:
                self.score += 1
                if self.left_wall.cells <= 20:
                    self.left_wall.cells += 1
                self.ball.color = random.choice(AVAIBLE_COLORS)
                self.left_wall.reset(self.ball.color)
                self.ball.speed_x *= -1

    def reset(self):
        self.score = 0
        self.game_over = False
        self.ball.x = WIDTH // 2
        self.ball.y = HEIGHT // 2
        self.ball.speed_y = 0
        self.ball.speed_x = -20
        self.left_wall.cells = 1
        self.right_wall.cells = 1
        self.left_wall.reset(self.ball.color)
        self.right_wall.reset(self.ball.color)

sim = simulation()

class input:
    def __init__(self):
        pass

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "SPACE"
                if event.key == pygame.K_r or event.key == pygame.K_SPACE:
                    sim.reset()
        return None

input_handler = input()

class Renderer:
    def __init__(self, screen, sim):
        self.screen = screen
        self.sim = sim

    def render(self):
        self.screen.fill((0, 0, 0))

        # Draw left wall
        for i in range(self.sim.left_wall.cells):
            pygame.draw.rect(self.screen, self.sim.left_wall.colors[i], (0, self.sim.left_wall.positions[i], WALL_WIDTH, self.sim.left_wall.size))

        # Draw right wall
        for i in range(self.sim.right_wall.cells):
            pygame.draw.rect(self.screen, self.sim.right_wall.colors[i], (WIDTH - WALL_WIDTH, self.sim.right_wall.positions[i], WALL_WIDTH, self.sim.right_wall.size))

        # Draw ball
        pygame.draw.circle(self.screen, self.sim.ball.color, (int(self.sim.ball.x), int(self.sim.ball.y)), self.sim.ball.radius)

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.sim.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

        pygame.display.flip()

    def render_game_over(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 72)
        game_over_text = font.render(f"Game Over\nScore: {self.sim.score}", True, (255, 0, 0))
        self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
        pygame.display.flip()

renderer = Renderer(screen, sim)

if __name__ == "__main__":
    while True:
        if not sim.game_over:
            user_input = input_handler.handle_input()
            if user_input:
                sim.ball.inputs(user_input)
            sim.update()
            renderer.render()  
        else:
            renderer.render_game_over()
            input_handler.handle_input()