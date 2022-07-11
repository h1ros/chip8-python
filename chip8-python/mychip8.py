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
SEED = 0xFF


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

    def load_game(self, path_rom: str):
        print(f'Loading ROM: {path_rom}')
        with open(path_rom, "rb") as f:
            for i in range(0, BUFFER_SIZE - 512):
                b = f.read(1) # read one hexadecimal and store as integer
                if b:
                    self.memory[i + 512] = int.from_bytes(b, 'big')
        
    def set_keys(self):
        pass
    
    def get_keys(self):
        pass

    def rand(self):
        return self.pc ^ SEED 
    
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
        self.opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
        print(f'self.opcode: {hex(self.memory[self.pc])[2:]} {hex(self.memory[self.pc+1])[2:]} ')
        self.pc += 2
        # Decode opcode
        if self.opcode & 0xFFFF == 0x00EE:
            # 00EE: return
            return            
        elif self.opcode & 0xFFF0 == 0x00E0:
            # 00E0: disp_clear()
            self.disp_clear()
        elif self.opcode & 0xF000 == 0x0000:
            # 0NNN: return;
            print(f'call machine code routine at {self.opcode & 0x0FFF}')            
        elif self.opcode & 0xF000 == 0x1000:
            # 1NNN: goto NNN;
            self.pc =  self.opcode & 0x0FFF
        elif self.opcode & 0xF000 == 0x2000:
            # 2NNN: *(0xNNN)()
            self.pc =  self.opcode & 0x0FFF
        elif self.opcode & 0xF000 == 0x3000:
            # 3XNN: if (Vx == NN)
            x = (self.opcode & 0x0F00) >> 8
            NN = self.opcode & 0x00FF 
            if self.V[x] == NN:
                self.pc += 2
        elif self.opcode & 0xF000 == 0x4000:
            # 4XNN: if (Vx != NN)
            x = (self.opcode & 0x0F00) >> 8
            NN = self.opcode & 0x00FF 
            if self.V[x] != NN:
                self.pc += 2
        elif self.opcode & 0xF000 == 0x5000:
            # 5XY0: if (Vx == Vy)
            x = (self.opcode & 0x0F00) >> 8
            y = (self.opcode & 0x00F0) >> 4
            if self.V[x] == self.V[y]:
                    self.pc += 2
        elif self.opcode & 0xF000 == 0x6000:
            # 6XNN: Sets VX to NN
            x = (self.opcode & 0x0F00) >> 8
            NN = self.opcode & 0x00FF 
            self.V[x] = NN
        elif self.opcode & 0xF000 == 0x7000:
            # 7XNN: Vx += NN
            x = (self.opcode & 0x0F00) >> 8
            NN = self.opcode & 0x00FF 
            self.V[x] += NN # Carry flag is not changed
        elif self.opcode & 0xF000 == 0x8000:
            x = (self.opcode & 0x0F00) >> 8
            y = (self.opcode & 0x00F0) >> 4
            case = self.opcode & 0x000F
            # 8XY0: Vx = Vy
            if case == 0:
                self.V[x] = self.V[y]
            # 8XY1: Vx |= Vy
            elif case == 1:
                self.V[x] |= self.V[y]
            # 8XY2: Vx &= Vy
            elif case == 2:
                self.V[x] &= self.V[y]           
            # 8XY3: Vx ^= Vy
            elif case == 3:
                self.V[x] ^= self.V[y]
            # 8XY4: Vx += Vy
            elif case == 4:
                if self.V[y] >  16 - self.V[x]:
                    self.V[0xF] = 1 # carry
                else:
                    self.V[0xF] = 0
                self.V[x] += self.V[y] 
            # 8XY5: Vx -= Vy
            elif case == 5:
                self.V[x] -= self.V[y]
            # 8XY6: Vx >>= Vy
            elif case == 6:
                self.V[x] >>= self.V[y]            
            # 8XY7: Vx = Vy - Vx
            elif case == 7:
                if self.V[x] < self.V[y]:
                    self.V[x] = 0  # TODO: check the behavior when it's below zero
                else:
                    self.V[x] = self.V[x] - self.V[y]            
            # 8XYE: Vx <<= 1
            elif case == 0xE:
                if self.V[x] > 128:
                    self.V[0xF] = 1 # carry
                else:
                    self.V[0xF] = 0 # carry
                self.V[x] <<= 1
        elif self.opcode & 0xF000 == 0x9000:
            # 9XY0: if (Vx != Vy)
            x = (self.opcode & 0x0F00) >> 8
            y = (self.opcode & 0x00F0) >> 4
            if self.V[x] != self.V[y]:
                    self.pc += 2
        elif self.opcode & 0xF000 == 0xA000:
            # ANNN: I = NNN (sets I to the adress NNN)
            self.I = self.opcode & 0x0FFF
        elif self.opcode & 0xF000 == 0xB000:
            # BNNN: PC = V0 + NNN (jumps to the adress NNN plus V0)
            self.pc = self.V[0] + self.opcode & 0x0FFF
        elif self.opcode & 0xF000 == 0xC000:
            # CXNN: Vx = rand() & NN
            x = (self.opcode & 0x0F00) >> 8
            NN = self.opcode & 0x00FF 
            self.V[x] = self.rand() + NN
        elif self.opcode & 0xF000 == 0xD000:
            # DXYN: draw(Vx, Vy, N)
            x = (self.opcode & 0x0F00) >> 8
            y = (self.opcode & 0x00F0) >> 4
            height = (self.opcode & 0x000F)
            self.draw(self.V[x],self.V[y], height)
        elif self.opcode & 0xF0FF == 0xE09E:
            # EX9E: if (key() == Vx)
            x = (self.opcode & 0x0F00) >> 8
            if self.key == self.V[x]:
                self.pc += 2
        elif self.opcode & 0xF0FF == 0xE0A1:
            # EXA1: if (key() != Vx)
            x = (self.opcode & 0x0F00) >> 8
            if self.key != self.V[x]:
                self.pc += 2
        elif self.opcode & 0xF0FF == 0xF007:
            # FX07: Vx = get_delay()
            x = (self.opcode & 0x0F00) >> 8
            self.delay_timer = x
        elif self.opcode & 0xF0FF == 0xF00A:
            # FX0A: Vx = get_key()
            x = (self.opcode & 0x0F00) >> 8
            self.V[x] = self.get_key()
        elif self.opcode & 0xF0FF == 0xF015:
            # FX15: delay_time(Vx)
            x = (self.opcode & 0x0F00) >> 8
            self.delay_timer = self.V[x]
        elif self.opcode & 0xF0FF == 0xF018:
            # FX18: sound_timer(Vx)
            x = (self.opcode & 0x0F00) >> 8
            self.sound_timer = self.V[x]
        elif self.opcode & 0xF0FF == 0xF01E:
            # FX1E: I += Vx
            x = (self.opcode & 0x0F00) >> 8
            self.I += self.V[x]
        elif self.opcode & 0xF0FF == 0xF029:
            # FX29: I = sprite_addr[Vx]
            x = (self.opcode & 0x0F00) >> 8
            self.I = self.V[x] # TODO: implement sprite_add[Vx]
        elif self.opcode & 0xF0FF == 0xF033:
            # FX33: set_BCD(Vx)
                    # *(I+0) = BCD(3);
                    # *(I+1) = BCD(2);
                    # *(I+2) = BCD(1);
            x = str((self.opcode & 0x0F00) >> 8).zfill(3)
            self.memory[self.I] = int(x[0])
            self.memory[self.I + 1] = int(x[1])
            self.memory[self.I + 2] = int(x[2])
        elif self.opcode & 0xF0FF == 0xF055:
            # FX55: reg_dump(Vx, &I)
            x = (self.opcode & 0x0F00) >> 8
            for i in range(0, self.V[x]+1): 
                self.memory[self.I + i] = self.V[i]
        elif self.opcode & 0xF0FF == 0xF065:
            # FX65: reg_load(Vx, &I)
            x = (self.opcode & 0x0F00) >> 8
            for i in range(0, self.V[x]+1): 
                self.V[i] = self.memory[self.I + i] 
        else:  
            raise('Unknown opcode: 0x%x\n' % self.opcode)
            
        # Update timers
        if (self.delay_timer > 0): 
            self.delay_timer -= 1
        if (self.sound_timer > 0): 
            if self.sound_timer == 1:
                print('Beep!\n')
            self.sound_timer -= 1
                
            