from mychip8 import MyChip8
import time
import argparse        

def main(path_rom):
    # Set up render system and register input callbacks
    setup_graphics()

    # Initialize the Chip8 system and load the game into the memory
    my_chip8 = MyChip8()
    my_chip8.load_game(path_rom=path_rom)

    # Emulation loop
    while True:
        print('Emulation Loop')
        time.sleep(.1)
        # Emulate one cycle
        my_chip8.emulate_cycle()

        # If the draw flag is set, update the screen
        if my_chip8.draw_flag:
            draw_graphics(my_chip8.gfx)

        # Store key press state (press and release)
        my_chip8.set_keys()


def setup_graphics():
    pass



def draw_graphics(gfx, t='■', f='□'):
    print(f'gfx: \n')
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
    print(graph)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Python-based Chip-8 Emulator')
    parser.add_argument('--path_rom', default='rom/pong.rom', dest='path_rom', help='File path for ROM (default: ./rom/pong.rom)')
    print(parser.parse_args())
    main(parser.parse_args().path_rom)
