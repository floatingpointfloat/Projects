from quadtree import QuadNode
from quadtree import QuadTree
import pygame
import random

pygame.init()
WIDTH, HEIGHT = 1000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quadtree Visualization")
quadtree = QuadTree(0, 0, WIDTH, HEIGHT)

#objects to insert into the quadtree
objects = []
for _ in range(1000):
    x = random.randint(0, WIDTH - 1)
    y = random.randint(0, HEIGHT - 1)
    quadtree.insert(x, y)
    objects.append((x, y))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            exit()
    
    screen.fill((0, 0, 0))
    for rect in quadtree.draw_tree():
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)
        
    for obj in objects:
        pygame.draw.circle(screen, (255, 0, 0), obj, 2)
           
    pygame.display.flip()