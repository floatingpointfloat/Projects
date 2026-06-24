import pygame
from sys import exit
import random

#initializing
pygame.init()
start_time = pygame.time.get_ticks()
WIDTH, HEIGHT = 50, 50
screen = pygame.display.set_mode((WIDTH * 9 + 10, HEIGHT + 10))

hotkeys = {
    '1': pygame.K_1, 
    '2': pygame.K_q, 
    '3': pygame.K_CAPSLOCK, 
    '4': pygame.K_4, 
    '5': pygame.K_e, 
    '6': pygame.K_f, 
    '7': pygame.K_c, 
    '8': pygame.K_v,
    '9': 2
}

if __name__ == '__main__':
    running = True
    new_slot = True
    required_input = None
    counter = -1
    while True:
        screen.fill((0, 0, 0))
        input = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                new_slot = True
                required_input = None
                counter = -1
                start_time = pygame.time.get_ticks()
            if required_input is not None:
                if event.type == pygame.KEYDOWN:
                    input = event.key
                if event.type == pygame.MOUSEBUTTONDOWN:
                    input = event.button
                
                if input in hotkeys.values():
                    if input == required_input:
                        new_slot = True
                    
        if running:
            if new_slot:
                random_slot =  random.randint(0,8)
                required_input = hotkeys.get(f"{random_slot + 1}") #gotta change the name here to change the dictionary - and obviusly the entire thing above
                new_slot = False
                counter += 1
            
            for i in range(9):
                if not i == random_slot:  
                    pygame.draw.rect(screen, (255, 255, 255), (i*WIDTH + 5, 5, WIDTH, HEIGHT), width=2)
                else:
                    pygame.draw.rect(screen, (255, 0, 0), (i*WIDTH + 5, 5, WIDTH, HEIGHT), width=5)
                        
        pygame.display.update()
        current_time = pygame.time.get_ticks()
        time_since_start = round((current_time - start_time) / 1000, 0)
        if counter != 0:
            pygame.display.set_caption(f"Hotkeys | Correct: {counter} | {time_since_start}s | Average per hotkey: {round(time_since_start / counter, 1)}s")
        else:
            pygame.display.set_caption(f"Hotkeys | Correct: {counter} | {time_since_start}s")
