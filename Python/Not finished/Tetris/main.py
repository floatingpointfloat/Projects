import math
import numpy as np
import time
import pygame
from sys import exit

WIDTH = 10
HEIGHT = 20
tiles = np.zeros((HEIGHT,WIDTH), dtype=int)
pixels_per_tile = 50
screen_width = WIDTH * pixels_per_tile
screen_height = HEIGHT * pixels_per_tile

block_tetromino = np.ones((2,2), dtype=int)
line_tetromino_vertical = np.array([[0, 1, 0, 0],
                                    [0, 1, 0, 0],
                                    [0, 1, 0, 0],
                                    [0, 1, 0, 0]],
                                   dtype=int)
T_tetromino = np.array([[1,1,1],
                        [0,1,0]],
                       dtype=int)
L_tetromino = np.array([[1,0],
                        [1,0],
                        [1,1]],
                       dtype=int)
L_reverse_tetromino = np.array([[0,1],
                                [0,1],
                                [1,1]],
                               dtype=int)
left_zigzag_tetromino = np.array([[1,1,0],
                                  [0,1,1]],
                                 dtype=int)
right_zigzag_tetromino = np.array([[0,1,1],
                                   [1,1,0]],
                                  dtype=int)
tetrominos = [{"shape": block_tetromino, "color": (255, 0, 0), "color_index": 1},
              {"shape": line_tetromino_vertical, "color": (0, 255, 0), "color_index": 2},
              {"shape": T_tetromino, "color": (0, 0, 255), "color_index": 3},
              {"shape": L_tetromino, "color": (255, 255, 0), "color_index": 4},
              {"shape": L_reverse_tetromino, "color": (255, 0, 255), "color_index": 5},
              {"shape": left_zigzag_tetromino, "color": (0, 255, 255), "color_index": 6},
              {"shape": right_zigzag_tetromino, "color": (200,200,200), "color_index": 7}]
colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),(200,200,200)]
tetromino_x, tetromino_y = 4, 0
speed = 0.5
score = 0

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

def draw_tiles():
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if tiles[y][x] != 0:
                pygame.draw.rect(screen, colors[tiles[y][x]-1], (x * pixels_per_tile, y * pixels_per_tile, pixels_per_tile, pixels_per_tile), 0)

def new_tetromino():
    global tetromino_x, tetromino_y
    tetromino_x, tetromino_y = 4, 0
    return tetrominos[np.random.randint(len(tetrominos))]

def check_collision(tetromino, x, y):
    for i in range(tetromino["shape"].shape[0]):
        for j in range(tetromino["shape"].shape[1]):
            if tetromino["shape"][i][j] != 0:
                if (y + i >= HEIGHT) or (x + j < 0) or (x + j >= WIDTH) or (tiles[y + i][x + j] != 0):
                    return True
    return False

def move_tetromino(tetromino, dx, dy):
    global tetromino_x, tetromino_y
    new_x = tetromino_x + dx
    new_y = tetromino_y + dy
    if not check_collision(tetromino, new_x, new_y):
        tetromino_x, tetromino_y = new_x, new_y

def rotate_tetromino(tetromino):
    global tetromino_x, tetromino_y
    rotated_shape = np.rot90(tetromino["shape"], -1)  # Rotate clockwise
    for dx in [0, -1, 1, -2, 2]:  # Try shifting left and right to fit the rotated piece
        if not check_collision({"shape": rotated_shape, 'color': tetromino['color']}, tetromino_x + dx, tetromino_y):
            tetromino["shape"] = rotated_shape
            tetromino_x += dx
            return

def merge(tetromino):
    for i in range(tetromino["shape"].shape[0]):
        for j in range(tetromino["shape"].shape[1]):
            if tetromino["shape"][i][j] != 0:
                tiles[tetromino_y + i][tetromino_x + j] = tetromino["color_index"]

def lock_tetromino():
    global current_tetromino
    merge(current_tetromino)
    current_tetromino = new_tetromino()

def draw_tetromino(tetromino):
    for i in range(tetromino["shape"].shape[0]):
        for j in range(tetromino["shape"].shape[1]):
            if tetromino["shape"][i][j] != 0:
                pygame.draw.rect(screen, tetromino["color"], ((tetromino_x + j) * pixels_per_tile, (tetromino_y + i) * pixels_per_tile, pixels_per_tile, pixels_per_tile), 0)

def check_line_clear():
    global tiles, speed, score
    for i in range(HEIGHT):
        if all(tiles[i] != 0):
            tiles[1:i+1] = tiles[0:i]  # Shift down all lines above
            tiles[0] = np.zeros(WIDTH, dtype=int)  # Clear the top line
            if speed > 0.2:
              speed -= 0.015
            score += 1
            print(f"Score: {score}, Speed: {speed:.2f}")

def draw_shadow(tetromino):
  global tetromino_x, tetromino_y
  x, y = tetromino_x, tetromino_y
  for i in range(HEIGHT):
    if not check_collision(tetromino, x, y):
      y += 1
    else:
      break
  for i in range(tetromino['shape'].shape[0]):
    for j in range(tetromino["shape"].shape[1]):
      if tetromino["shape"][i][j] != 0:
        pygame.draw.rect(screen, (50,50,50), ((x + j)*pixels_per_tile, (y + i - 1)*pixels_per_tile, pixels_per_tile, pixels_per_tile), 0)

def gameover():
  global tiles
  if any(tiles[0] != 0):
    return True
  return False

#Main loop
if __name__ == "__main__":
    current_tetromino = new_tetromino() # Start with a random tetromino
    start_time = time.time()
    running = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_tetromino(current_tetromino, -1, 0)
                elif event.key == pygame.K_RIGHT:
                    move_tetromino(current_tetromino, 1, 0)
                elif event.key == pygame.K_DOWN:
                    move_tetromino(current_tetromino, 0, 1)
                elif event.key == pygame.K_UP:
                    rotate_tetromino(current_tetromino)
                elif event.key == pygame.K_SPACE:
                  for i in range(HEIGHT):
                    move_tetromino(current_tetromino, 0, 1)

        screen.fill((0, 0, 0))  # Clear the screen with black

        draw_tiles()  # Draw the tiles on the screen
        if running:
            draw_shadow(current_tetromino) #Draw the shadow of the tetromino
            draw_tetromino(current_tetromino)  # Draw the current tetromino
            if time.time() - start_time > speed:  # Move down according to the speed
                if not check_collision(current_tetromino, tetromino_x, tetromino_y + 1):
                    move_tetromino(current_tetromino, 0, 1)
                else:
                    lock_tetromino()  # Lock the tetromino in place
                    if gameover():
                        running = False
                    check_line_clear()  # Check for line clears
                start_time = time.time()  # Reset the timer

        pygame.display.flip()
        clock.tick(60)  # Limit to 60 frames per second