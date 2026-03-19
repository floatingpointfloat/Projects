import pygame
from sys import exit
import math
import random

#setup
pygame.init()
screen = pygame.display.set_mode((618, 422))
pygame.display.set_caption("Pong :)")
clock = pygame.time.Clock()

#variables:
bat1_y = 211
bat2_y = 211
bat1_angle = 0
bat2_angle = 0

ball_y = 211
ball_x = 309
ball_pos = pygame.Vector2(ball_x, ball_y)
speed = 4
ball_vel = pygame.Vector2(-4, -2.5)

score1 = 0
score2 = 0

#normalen:
#decken
ceiling_normal = pygame.Vector2(0, 1)
floor_normal = pygame.Vector2(0, -1)
#bats
bat1_0_normal = pygame.Vector2(1, 0)
bat1_15_normal = pygame.Vector2(1, 0).rotate(-15)
bat1_negative_15_normal = pygame.Vector2(1, 0).rotate(15)
bat2_0_normal = pygame.Vector2(-1, 0)
bat2_15_normal = pygame.Vector2(-1, 0).rotate(-15)
bat2_negative_15_normal = pygame.Vector2(-1, 0).rotate(15)

#objects:
background_surf = pygame.image.load("background.png")
font = pygame.font.Font("Pixeltype.ttf", False)
score_1_surf = font.render(f"{score1 - 1}", False, (255, 255, 255))
score_1_rect = score_1_surf.get_rect()
score_1_rect.topright = (309, 10)
score_2_surf = font.render(f"{score2 - 1}", False, (255, 255, 255))
score_2_rect = score_2_surf.get_rect()
score_2_rect.topleft = (309, 10)

bat1_surf = pygame.image.load("bat.png").convert_alpha()
bat1_rect = bat1_surf.get_rect()
bat2_surf = pygame.image.load("bat.png").convert_alpha()
bat2_rect = bat2_surf.get_rect()
ball_surf = pygame.image.load("ball.png").convert_alpha()
ball_surf = pygame.transform.scale(ball_surf, (10, 10))
ball_rect = ball_surf.get_rect()

def score():
    global score1, score2, bat1_y, bat2_y
    screen.blit(score_1_surf, score_1_rect)

while True:
    #keys
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
            pygame.quit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and bat1_rect.top > 0:
        bat1_y -= 10
    if keys[pygame.K_s] and bat1_rect.bottom < 422:
        bat1_y += 10
    if keys[pygame.K_UP] and bat2_rect.top > 0:
        bat2_y -= 10
    if keys[pygame.K_DOWN] and bat2_rect.bottom < 422:
        bat2_y += 10
    if keys[pygame.K_a] and bat1_angle < 15:
        bat1_angle = 15
    if keys[pygame.K_d] and bat1_angle > -15:
        bat1_angle = -15
    if keys[pygame.K_LEFT] and bat2_angle < 15:
        bat2_angle = 15
    if keys[pygame.K_RIGHT] and bat2_angle > -15:
        bat2_angle = -15

    #ball collisions:
    #ceiling/floor
    if ball_rect.top <= 0 and ball_vel.y < 0:
        ball_vel = ball_vel.reflect(ceiling_normal)
        ball_vel = ball_vel.normalize() * speed
    if ball_rect.bottom >= 422 and ball_vel.y > 0:
        ball_vel = ball_vel.reflect(floor_normal)
        ball_vel = ball_vel.normalize() * speed

    #bats
    if ball_rect.colliderect(bat1_rect) and ball_vel.x < 0:
        if bat1_angle == 0:
            ball_vel = ball_vel.reflect(bat1_0_normal)
            ball_vel = ball_vel.normalize() * speed
        if bat1_angle == 15:
            if ball_vel.y / ball_vel.x <= 1.5:
                ball_vel = ball_vel.reflect(bat1_15_normal)
            else:
                ball_vel = ball_vel.reflect(bat1_0_normal)
            ball_vel = ball_vel.normalize() * speed
        if bat1_angle == -15:
            if ball_vel.y / ball_vel.x >= -1.5:
                ball_vel = ball_vel.reflect(bat1_negative_15_normal)
            else:
                ball_vel = ball_vel.reflect(bat1_0_normal)
            ball_vel = ball_vel.normalize() * speed

    if ball_rect.colliderect(bat2_rect) and ball_vel.x > 0:
        if bat2_angle == 0:
            ball_vel = ball_vel.reflect(bat2_0_normal)
            ball_vel = ball_vel.normalize() * speed
        if bat2_angle == 15:
            if ball_vel.y / ball_vel.x <= 1.5:
                ball_vel = ball_vel.reflect(bat2_15_normal)
            else:
                ball_vel = ball_vel.reflect(bat2_0_normal)
            ball_vel = ball_vel.normalize() * speed
        if bat2_angle == -15:
            if ball_vel.y / ball_vel.x >= -1.5:
                ball_vel = ball_vel.reflect(bat2_negative_15_normal)
            else:
                ball_vel = ball_vel.reflect(bat2_0_normal)
            ball_vel = ball_vel.normalize() * speed

    #reset
    if ball_rect.midleft[0] <= 0 and ball_vel.x < 0:
        score2 += 1
        ball_pos = (309, 211)
        speed = 4
    if ball_rect.midright[0] >= 618 and ball_vel.x > 0:
        score1 += 1
        ball_pos = (309, 211)
        speed = 4

    screen.blit(background_surf, (0, 0) )

    bat1_rect.midleft = (0, bat1_y)
    screen.blit(bat1_surf, bat1_rect)
    bat2_rect.midright = (618, bat2_y)
    screen.blit(bat2_surf, bat2_rect)
    ball_rect.center = (ball_pos[0], ball_pos[1])
    screen.blit(ball_surf, ball_rect)

    #variable update:
    ball_pos += ball_vel
    bat1_angle = 0
    bat2_angle = 0

    speed += 0.004

    pygame.display.update()
    clock.tick(60)