from mychip8 import MyChip8
import time

stack = [0 for _ in range(16)]  # unsigned short
sp = 0  # unsigned short
key = [0 for _ in range(16)]  # unsigned char

def main(argc: int, **argv):
    # Set up render system and register input callbacks
    setup_graphics()
    setup_input()

    # Initialize the Chip8 system and load the game into the memory
    my_chip8 = MyChip8()
    my_chip8.load_game(game_name="rom/test_opcode.ch8")

    # Emulation loop
    while True:
        print('Emulation Loop')
        time.sleep(1)
        # Emulate one cycle
        my_chip8.emulate_cycle()

        # If the draw flag is set, update the screen
        if my_chip8.draw_flag:
            draw_graphics(my_chip8.gfx)

        # Store key press state (press and release)
        my_chip8.set_keys()


def setup_graphics():
    pass


def setup_input():
    pass


def draw_graphics(gfx, t='*', f=' '):
    print(f'gfx: \n')
    graph = '-' * 64 + '\n'
    for i, e in enumerate(gfx):
        if i % 64 == 0:
            graph += '\n'
        if e:
            graph += t
        else:
            graph += f
    graph += '\n'    
    graph += '-' * 64
    print(graph)


if __name__ == "__main__":
    main(0)
