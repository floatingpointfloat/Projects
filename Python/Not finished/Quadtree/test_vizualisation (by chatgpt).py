from quadtree import QuadTree
import pygame
import random
import math

pygame.init()
WIDTH, HEIGHT = 1000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quadtree Visualization - Moving Points")
clock = pygame.time.Clock()

# Quadtree
quadtree = QuadTree(0, 0, WIDTH, HEIGHT)

# bewegliche Objekte: (x, y, vx, vy)
objects = []
for _ in range(1000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)

    angle = random.uniform(0, math.tau)
    speed = random.uniform(0.3, 1.5)

    vx = math.cos(angle) * speed
    vy = math.sin(angle) * speed

    objects.append([x, y, vx, vy])


SEARCH_RADIUS = 60

running = True
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # -------------------------
    # Bewegung + Randabprall
    # -------------------------
    for obj in objects:
        obj[0] += obj[2]
        obj[1] += obj[3]

        x, y, vx, vy = obj

        if x < 0 or x > WIDTH:
            obj[2] *= -1
        if y < 0 or y > HEIGHT:
            obj[3] *= -1

    # -------------------------
    # Quadtree neu aufbauen
    # -------------------------
    quadtree.clear()
    for obj in objects:
        quadtree.insert(obj[0], obj[1])

    # -------------------------
    # Rendering
    # -------------------------
    screen.fill((0, 0, 0))

    # Quadtree-Gitter
    for rect in quadtree.draw_tree():
        pygame.draw.rect(screen, (60, 60, 60), rect, 1)

    # Punkte
    for obj in objects:
        pygame.draw.circle(screen, (255, 80, 80), (int(obj[0]), int(obj[1])), 2)

    # -------------------------
    # Debug: Query-Kreis (Maus)
    # -------------------------
    mx, my = pygame.mouse.get_pos()
    nearby = quadtree.query(mx, my, SEARCH_RADIUS)

    # Kreis anzeigen
    pygame.draw.circle(screen, (0, 150, 255), (mx, my), SEARCH_RADIUS, 1)

    # gefundene Punkte highlighten
    for px, py in nearby:
        pygame.draw.circle(screen, (0, 255, 0), (int(px), int(py)), 3)

    pygame.display.flip()

pygame.quit()
