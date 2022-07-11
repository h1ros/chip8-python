# fmt: off
CHIP8_FONTSET = \
[ 
  0xF0, 0x90, 0x90, 0x90, 0xF0, ## 0
  0x20, 0x60, 0x20, 0x20, 0x70, ## 1
  0xF0, 0x10, 0xF0, 0x80, 0xF0, ## 2
  0xF0, 0x10, 0xF0, 0x10, 0xF0, ## 3
  0x90, 0x90, 0xF0, 0x10, 0x10, ## 4
  0xF0, 0x80, 0xF0, 0x10, 0xF0, ## 5
  0xF0, 0x80, 0xF0, 0x90, 0xF0, ## 6
  0xF0, 0x10, 0x20, 0x40, 0x40, ## 7
  0xF0, 0x90, 0xF0, 0x90, 0xF0, ## 8
  0xF0, 0x90, 0xF0, 0x10, 0xF0, ## 9
  0xF0, 0x90, 0xF0, 0x90, 0x90, ## A
  0xE0, 0x90, 0xE0, 0x90, 0xE0, ## B
  0xF0, 0x80, 0x80, 0x80, 0xF0, ## C
  0xE0, 0x90, 0x90, 0x90, 0xE0, ## D
  0xF0, 0x80, 0xF0, 0x80, 0xF0, ## E
  0xF0, 0x80, 0xF0, 0x80, 0x80  ## F
]
# fmt: on
BUFFER_SIZE = 4096



class MyChip8(object):

    draw_flag = 0

    def __init__(self):
        """Initialize registers and memory once"""
        self.pc = 0x200  # program counter starts at 0x200 (=512)
        self.opcode = 0  # initial opcode
        self.I = 0  # index register
        self.sp = 0  # stack pointer
        self.V = [0] * 16 # register
        self.memory = [0] * BUFFER_SIZE # memory

        # Clear display
        self.gfx = [0] * (64 * 32)

        # Clear stack
        # Clear registers V0-VF
        # Clear memory

        # Load fontset
        for i in range(0, len(CHIP8_FONTSET)):
            self.memory[i] = CHIP8_FONTSET[i]

        # Reset timers
        self.delay_timer = 0
        self.sound_timer = 0

    def load_game(self, game_name: str):

        with open(game_name, "rb") as f:
            for i in range(0, BUFFER_SIZE - 512):
                b = f.read(1) # read one hexadecimal and store as integer
                if b:
                    self.memory[i + 512] = int.from_bytes(b, 'big')
        
    def set_keys(self):
        pass
    
    def draw(self, Vx, Vy, height):
        self.V[0xF] = 0
        for y in range(0, height):
            pixel = self.memory[self.I + y]
            for x in range(0, 8):
                if (pixel  & (0x80 >> x)) != 0:
                    if self.gfx[(Vx + x + ((Vy + y) * 64)) == 1]:
                        self.V[0xF] = 1
                    self.gfx[Vx + x + ((Vy + y) * 64)] ^= 1
        
        self.draw_flag = 1
        self.pc += 2
        

    def emulate_cycle(self):
        """Proceed one cycle of emulater following the steps below:
        1. Fetch Opcode
        2. Decode Opcode
        3. Execute Opcode
        4. Update timers
        """
        # Fetch opcode
        self.opcode = self.memory[self.pc] << 8 | self.memory[self.pc]
        print(f'self.opcode: {self.opcode}')
        # Decode opcode
        if self.opcode & 0xF000 == 0xA000:
            # ANNN: sets I to the adress NNN
            self.I = self.opcode & 0x0FFF
            self.pc += 2
        elif self.opcode & 0xF000 == 0xB000:
            # BNNN: jumps to the adress NNN plus V0
            self.pc = self.V[0] + self.opcode & 0x0FFF
        elif self.opcode & 0xF000 == 0x6000:
            # 6XNN: Sets VX to NN.
            self.V[(self.opcode & 0x0F00) >> 8] = self.opcode & 0x00FF
        elif self.opcode & 0xF000 == 0xD000:
            # DXYN: draw(Vx, Vy, N)
            x = (self.opcode & 0x0F00) >> 8
            y = (self.opcode & 0x00F0) >> 4
            height = (self.opcode & 0x000F)
            self.draw(self.V[x],self.V[y], height)
    
        else:  
            print('Unknown opcode: 0x%x\n' % self.opcode)

        # Update timers
        if (self.delay_timer > 0): 
            self.delay_timer -= 1
        if (self.sound_timer > 0): 
            if self.sound_timer == 1:
                print('Beep!\n')
            self.sound_timer -= 1
                
            