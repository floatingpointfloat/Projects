import pygame
from sys import exit
import random


#global variables:
gravity =  2
start_screen = True
global score
score = 0
#positions
global pos_1_y
global pos_1_x
global pos_2_y
global pos_2_x
global pos_3_y
global pos_3_x
global new_pos_1
global new_pos_2
global new_pos_3
pos_1_y = 200
pos_1_x = 750
new_pos_1 = True
pos_2_y = 200
pos_2_x = 950
new_pos_2 = True
pos_3_y = 200
pos_3_x = 1150
new_pos_3 = True

#setup
pygame.init()
screen = pygame.display.set_mode((700, 400))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
font = pygame.font.Font("Pixeltype.ttf", 50)

#surfaces
bird_surf = pygame.image.load('bird.PNG').convert_alpha()
bird_surf = pygame.transform.rotozoom(bird_surf, 0, 0.08)
bird_rect = bird_surf.get_rect()
bird_rect.x = 100
bird_rect.y = 250
background_1_surf = pygame.image.load("background.JPG")
background_1_rect = background_1_surf.get_rect()
background_2_surf = pygame.image.load("background.JPG")
background_2_rect = background_2_surf.get_rect()
#start screen
game_message = font.render("Press SPACE to play",False,(10,10,10))
game_message_rect = game_message.get_rect(center = (350,250))
game_name = font.render("Flappy Bird",False,(10,10,10))
game_name_rect = game_name.get_rect(center = (350,150))
#score
score_surf = font.render(f"Score : {score}",False,(10,10,10))
score_rect = score_surf.get_rect(center = (350,30))
#pipes
pipe_up_1_surf = pygame.image.load('up.PNG')
pipe_up_1_surf = pygame.transform.rotozoom(pipe_up_1_surf, 0, 0.1)
pipe_up_1_rect = pipe_up_1_surf.get_rect()
pipe_up_2_surf = pygame.image.load('up.PNG').convert_alpha()
pipe_up_2_surf = pygame.transform.rotozoom(pipe_up_2_surf, 0, 0.1)
pipe_up_2_rect = pipe_up_2_surf.get_rect()
pipe_up_3_surf = pygame.image.load('up.PNG').convert_alpha()
pipe_up_3_surf = pygame.transform.rotozoom(pipe_up_3_surf, 0, 0.1)
pipe_up_3_rect = pipe_up_3_surf.get_rect()
pipe_down_1_surf = pygame.image.load('down.PNG').convert_alpha()
pipe_down_1_surf = pygame.transform.rotozoom(pipe_down_1_surf, 0, 0.1)
pipe_down_1_rect = pipe_down_1_surf.get_rect()
pipe_down_2_surf = pygame.image.load('down.PNG').convert_alpha()
pipe_down_2_surf = pygame.transform.rotozoom(pipe_down_2_surf, 0, 0.1)
pipe_down_2_rect = pipe_down_2_surf.get_rect()
pipe_down_3_surf = pygame.image.load('down.PNG').convert_alpha()
pipe_down_3_surf = pygame.transform.rotozoom(pipe_down_3_surf, 0, 0.1)
pipe_down_3_rect = pipe_down_3_surf.get_rect()

def score_update():
    global score
    global start_screen
    if abs(bird_rect.x - pipe_up_1_rect.x) < 10 and bird_rect.x > pipe_up_1_rect.x:
        score += 1
    if abs(bird_rect.x - pipe_up_2_rect.x) < 10 and bird_rect.x > pipe_up_2_rect.x:
        score += 1
    if abs(bird_rect.x - pipe_up_3_rect.x) < 10 and bird_rect.x > pipe_up_3_rect.x:
        score += 1
    score_surf = font.render(f"Score : {score}", False, (10,10,10))
    score_rect = score_surf.get_rect(center=(350, 30))
    screen.blit(score_surf, score_rect)

#pos_1_y, pos_2_y, pos_3_y, pos_1_x, pos_2_x, pos_3_x
def random_pos():
    global pos_1_y
    global pos_1_x
    global pos_2_y
    global pos_2_x
    global pos_3_y
    global pos_3_x
    global new_pos_1
    global new_pos_2
    global new_pos_3
    if new_pos_1 == True:
        pos_1_y = int(random.randint(100, 300))
        pos_1_x = pos_3_x + 300
        new_pos_1 = False
    if new_pos_2 == True:
        pos_2_y = int(random.randint(100, 300))
        pos_2_x = pos_1_x +300
        new_pos_2 = False
    if new_pos_3 == True:
        pos_3_y = int(random.randint(100, 300))
        pos_3_x = pos_2_x + 300
        new_pos_3 = False

random_pos()

#gameloop:
while True:
    #keys
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                gravity = -5
                start_screen = False

    #collisions:
    if bird_rect.colliderect(pipe_up_1_rect):
        print(score)
        exit()
        pygame.quit()
    if bird_rect.colliderect(pipe_up_2_rect):
        print(score)
        exit()
        pygame.quit()
    if bird_rect.colliderect(pipe_up_3_rect):
        print(score)
        exit()
        pygame.quit()
    if bird_rect.colliderect(pipe_down_1_rect):
        print(score)
        exit()
        pygame.quit()
    if bird_rect.colliderect(pipe_down_2_rect):
        print(score)
        exit()
        pygame.quit()
    if bird_rect.colliderect(pipe_down_3_rect):
        print(score)
        exit()
        pygame.quit()
    if bird_rect.y > 400 or bird_rect.y < 0:
        print(score)
        exit()
        pygame.quit()

    #pipe positions setup
    pipe_up_1_rect.left = pos_1_x
    pipe_down_1_rect.left = pos_1_x
    pipe_up_1_rect.bottom = pos_1_y - 45
    pipe_down_1_rect.top = pos_1_y + 45

    pipe_up_2_rect.left = pos_2_x
    pipe_down_2_rect.left = pos_2_x
    pipe_up_2_rect.bottom = pos_2_y - 45
    pipe_down_2_rect.top = pos_2_y + 45

    pipe_up_3_rect.left = pos_3_x
    pipe_down_3_rect.left = pos_3_x
    pipe_up_3_rect.bottom = pos_3_y - 45
    pipe_down_3_rect.top = pos_3_y + 45


    #pos_reset:
    if pipe_up_1_rect.right < 0:
        new_pos_1 = True
        random_pos()
    if pipe_up_2_rect.right < 0:
        new_pos_2 = True
        random_pos()
    if pipe_up_3_rect.right < 0:
        new_pos_3 = True
        random_pos()

    if start_screen:
        screen.fill((255,255,255))
        screen.blit(game_message, game_message_rect)
        screen.blit(game_name, game_name_rect)
    else:
        screen.blit(background_1_surf, (0, 0))
        screen.blit(pipe_up_1_surf, pipe_up_1_rect)
        screen.blit(pipe_down_1_surf, pipe_down_1_rect)
        screen.blit(pipe_up_2_surf, pipe_up_2_rect)
        screen.blit(pipe_down_2_surf, pipe_down_2_rect)
        screen.blit(pipe_up_3_surf, pipe_up_3_rect)
        screen.blit(pipe_down_3_surf, pipe_down_3_rect)
        screen.blit(bird_surf, bird_rect)

        # variables update
        gravity += 0.3
        pos_1_x -= 5
        pos_2_x -= 5
        pos_3_x -= 5

        bird_rect.y += gravity
        score_update()

    pygame.display.update()
    clock.tick(60)