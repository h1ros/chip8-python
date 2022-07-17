from mychip8 import MyChip8
import time
import argparse        
import os
import tkinter as tk
import pygame
import sys

BLACK = (40, 40, 40)
WHITE = (200, 200, 200)
WINDOW_HEIGHT = 320
WINDOW_WIDTH = 640



def main(path_rom):
    # Set up render system and register input callbacks
    setup_graphics()

    # Initialize the Chip8 system and load the game into the memory
    my_chip8 = MyChip8()
    my_chip8.load_game(path_rom=path_rom)

    # Emulation loop
    while True:
        # print('Emulation Loop')
        # time.sleep(.1)
        # Emulate one cycle
        my_chip8.emulate_cycle()

        # If the draw flag is set, update the screen
        if my_chip8.draw_flag:
            # os.system('clear')
            draw_graphics_pygame(my_chip8.gfx)

        # Store key press state (press and release)
        my_chip8.set_keys()


def setup_graphics():
    global SCREEN, CLOCK
    pygame.init()
    CLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    SCREEN.fill(BLACK)

def draw_graphics(gfx, t='■', f='□'):
    # print(f'gfx: \n')
    graph = '-' * 64 + '\n'
    row = 0
    for i, e in enumerate(gfx):
        if i % 64 == 0:
            graph += f'\n row {str(row).zfill(2)}   '
            row += 1
        elif i % 8 == 0:
            graph += '|'    
        if e:
            graph += t
        else:
            graph += f
    graph += '\n'    
    graph += '-' * 64
    print(graph, end='\r', flush=True)


def draw_graphics_pygame(gfx):


    blockSize = 10 #Set the size of the grid block
    for i, e in enumerate(gfx):
        x = (i % 64) * blockSize
        y = (i // 64) * blockSize
        rect = pygame.Rect(x, y, blockSize, blockSize)
        if e:
            pygame.draw.rect(SCREEN, WHITE, rect, 0)
            
        else:
            pygame.draw.rect(SCREEN, BLACK, rect, 0)
                        
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()



    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Python-based Chip-8 Emulator')
    parser.add_argument('--path_rom', default='rom/pong.rom', dest='path_rom', help='File path for ROM (default: ./rom/pong.rom)')
    main(parser.parse_args().path_rom)
