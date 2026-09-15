import pygame
from sys import exit
import random
import time

#variables
WIDTH, HEIGHT = 50, 50
pixels_per_tile = 15
snake_length = 1
snake_body = []
snake_head_x, snake_head_y = WIDTH // 2, HEIGHT // 2
direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
next_direction = direction
speed = 0.15
score = 0
food_x, food_y, food_color = 0, 0, (255, 0, 0)

#initializing pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH * pixels_per_tile, HEIGHT * pixels_per_tile))
pygame.display.set_caption("snake :)")
clock = pygame.time.Clock()
start_time = time.time()
font = pygame.font.SysFont("Arial", 20)

def grow():
    global snake_length, score, speed
    snake_length += 1
    score += 1
    if speed > 0.01:
        speed -= 0.01

def check_collision():
    global snake_body, snake_head_x, snake_head_y, running
    if snake_head_x < 0 or snake_head_x >= WIDTH or snake_head_y < 0 or snake_head_y >= HEIGHT:
        running = False
        return True
    if (snake_head_x, snake_head_y) in snake_body:
        running = False 
        return True
    else:
        return False

def move_snake():
    global snake_head_x, snake_head_y, snake_body, snake_length, direction
    direction = next_direction
    if direction == "UP":
        snake_head_y -= 1
    elif direction == "DOWN":
        snake_head_y += 1
    elif direction == "LEFT":
        snake_head_x -= 1
    elif direction == "RIGHT":
        snake_head_x += 1
    if not check_collision():
        snake_body.append((snake_head_x, snake_head_y))
        if len(snake_body) > snake_length:
            snake_body.pop(0)

def spawn_food():
    while True:
        food_x = random.randint(0, WIDTH - 1)
        food_y = random.randint(0, HEIGHT - 1)
        if (food_x, food_y) not in snake_body and (food_x, food_y) != (snake_head_x, snake_head_y):
            return food_x, food_y
        
def check_food():
    global snake_head_x, snake_head_y, food_x, food_y
    if (snake_head_x, snake_head_y) == (food_x, food_y):
        grow()
        food_x, food_y = spawn_food()


def is_opposite_direction(current_direction, candidate_direction):
    opposites = {
        "UP": "DOWN",
        "DOWN": "UP",
        "LEFT": "RIGHT",
        "RIGHT": "LEFT",
    }
    return opposites[current_direction] == candidate_direction
    
    
if __name__ == "__main__":
    food_x, food_y = spawn_food()
    running = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                queued_direction = None
                if event.key == pygame.K_UP:
                    queued_direction = "UP"
                elif event.key == pygame.K_DOWN:
                    queued_direction = "DOWN"
                elif event.key == pygame.K_LEFT:
                    queued_direction = "LEFT"
                elif event.key == pygame.K_RIGHT:
                    queued_direction = "RIGHT"
                if queued_direction and not is_opposite_direction(direction, queued_direction):
                    next_direction = queued_direction
                elif event.key == pygame.K_SPACE and not running:
                    snake_head_x, snake_head_y = WIDTH // 2, HEIGHT // 2
                    snake_body = []
                    snake_length, score, speed = 1, 0, 0.15
                    direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
                    next_direction = direction
                    food_x, food_y = spawn_food()
                    running = True
                    
        screen.fill((0, 0, 0))
        if running:
            if time.time() - start_time > speed:
                move_snake()
                check_food()
                start_time = time.time()
        
        screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
        pygame.draw.rect(screen, food_color, (food_x * pixels_per_tile, food_y * pixels_per_tile, pixels_per_tile, pixels_per_tile))
        for x, y in snake_body:
            pygame.draw.rect(screen, (0, 170, 0), (x * pixels_per_tile, y * pixels_per_tile, pixels_per_tile, pixels_per_tile))
        pygame.draw.rect(screen, (0, 255, 0), (snake_head_x * pixels_per_tile, snake_head_y * pixels_per_tile, pixels_per_tile, pixels_per_tile))
        
        if not running:
            screen.blit(font.render(f"Game Over! Press Space to Restart.", True, (255, 255, 255)), (WIDTH * pixels_per_tile // 2 - 150, HEIGHT * pixels_per_tile // 2 - 10))
            
        pygame.display.flip()
        clock.tick(10)
