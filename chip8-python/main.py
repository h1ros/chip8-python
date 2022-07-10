
from mychip8 import MyChip8


# Memory

opcode = 0 # unsigned short
memory = [0 for _ in range(4096)] # unsigned char
V = [0 for _ in range(16)]
I = 0 # unsinged short
pc = 0 # unsigned short 

gfx = [0 for _ in range(64 * 32)]
delay_timer = 0 # unsigned char
sound_timer = 0 # unsigned char

stack = [0 for _ in range(16)] # unsigned short
sp = 0 # unsigned short
key = [0 for _ in range(16)] # unsigned char

def main(argc: int, **argv):
    # Set up render system and register input callbacks
    setup_graphics()
    setup_input()

    # Initialize the Chip8 system and load the game into the memory 
    my_chip8 = MyChip8()
    my_chip8.load_game(game_name='pong')

    # Emulation loop
    while True:

        # Emulate one cycle
        my_chip8.emulate_cycle()

        # If the draw flag is set, update the screen
        if my_chip8.draw_flag:
            draw_graphics()

        # Store key press state (press and release)
        my_chip8.set_keys()






def setup_graphics():
    pass

def setup_input():
    pass

def draw_graphics():
    pass

if __name__ == "__main__":
    main(0)