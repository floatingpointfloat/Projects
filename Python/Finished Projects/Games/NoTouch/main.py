import random
import pygame
from sys import exit
from pathlib import Path

WIDTH,HEIGHT = 800,600
G = 800
AVAIBLE_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (128, 0, 128)]
WALL_WIDTH = 20
SPEED = -500

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Touch the correct color!")
clock = pygame.time.Clock()

highscore_file = Path(__file__).parent / "highscore.txt"

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

    def inputs(self, input, dt):
        if input == "SPACE":
            self.speed_y -= 3000 * dt
        if input == "SHIFT":
            self.speed_y += 2600 * dt

start_color = random.choice(AVAIBLE_COLORS)
ball = ball(WIDTH // 2, HEIGHT // 2, 5, start_color, 0, SPEED)

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
    def __init__(self, dt):
        self.left_wall = left_wall
        self.right_wall = right_wall
        self.ball = ball
        self.score = 0
        self.game_over = False
        self.G = G
        self.dt = dt
        self.new_highscore = False
        self.high_score = 0
        try:
            with open(highscore_file, "r") as f:
                self.high_score = int(f.read().strip())
        except FileNotFoundError:
            self.high_score = 0

    def update(self, dt):
        self.ball.update_position(dt)

        # Check for collisions with walls
        if self.ball.x - self.ball.radius <= WALL_WIDTH:
            if self.left_wall.collision(self.ball):
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.new_highscore = True

                    with open(highscore_file, "w") as f:
                        f.write(str(self.high_score))
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
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.new_highscore = True

                    with open(highscore_file, "w") as f:
                        f.write(str(self.high_score))
            else:
                self.score += 1
                if self.left_wall.cells <= 20:
                    self.left_wall.cells += 1
                self.ball.color = random.choice(AVAIBLE_COLORS)
                self.left_wall.reset(self.ball.color)
                self.ball.speed_x *= -1

        #in case the ball goes out of bounds vertically at a wall, reset the game
        if (self.ball.y + self.ball.radius <= 0 or self.ball.y - self.ball.radius >= HEIGHT) and (self.ball.x - self.ball.radius <= WALL_WIDTH or self.ball.x + self.ball.radius >= WIDTH - WALL_WIDTH):
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self.new_highscore = True
                with open(highscore_file, "w") as f:
                    f.write(str(self.high_score))

    def reset(self):
        self.score = 0
        self.game_over = False
        self.new_highscore = False
        self.ball.x = WIDTH // 2
        self.ball.y = HEIGHT // 2
        self.ball.speed_y = 0
        self.ball.speed_x = SPEED
        self.left_wall.cells = 1
        self.right_wall.cells = 1
        self.left_wall.reset(self.ball.color)
        self.right_wall.reset(self.ball.color)

sim = simulation(0.001)

class input:
    def __init__(self, sim):
        self.sim = sim

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if self.sim.game_over:
                    if event.key == pygame.K_r or event.key == pygame.K_SPACE:
                        self.sim.reset()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            return "SPACE"
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            return "SHIFT"
        return None

input_handler = input(sim)

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
        font = pygame.font.Font(None, 30)
        game_over_text = font.render(f"Game Over - Score: {self.sim.score} - High Score: {self.sim.high_score}", True, self.sim.ball.color)
        self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
        if self.sim.new_highscore:
            highscore_text = font.render("New High Score!", True, self.sim.ball.color)
            self.screen.blit(highscore_text, (WIDTH // 2 - highscore_text.get_width() // 2, HEIGHT // 2 + 50))
        pygame.display.flip()

renderer = Renderer(screen, sim)

if __name__ == "__main__":
    while True:
        dt = clock.tick(60) / 1000  # Limit to 60 FPS and get delta time in seconds
        if not sim.game_over:
            user_input = input_handler.handle_input()
            if user_input:
                sim.ball.inputs(user_input, dt)
            sim.update(dt)
            renderer.render()  
        else:
            renderer.render_game_over()
            input_handler.handle_input()