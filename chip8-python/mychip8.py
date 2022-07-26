import random
import logging
import keyboard

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('chip8.log', mode='w')
formatter = logging.Formatter('%(asctime)s : %(name)s  : %(funcName)s : %(levelname)s : %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

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
WIDTH = 64
HEIGHT = 32

# Keypad                   Keyboard
# +-+-+-+-+                +-+-+-+-+
# |1|2|3|C|                |1|2|3|4|
# +-+-+-+-+                +-+-+-+-+
# |4|5|6|D|                |Q|W|E|R|
# +-+-+-+-+       =>       +-+-+-+-+
# |7|8|9|E|                |A|S|D|F|
# +-+-+-+-+                +-+-+-+-+
# |A|0|B|F|                |Z|X|C|V|
# +-+-+-+-+                +-+-+-+-+
KEY_MAP = {c: i for i, c in enumerate('x123qweasdzc4rfv')}

class MyChip8(object):


    def __init__(self):
        """Initialize registers and memory once"""
        self.pc = 0x200  # program counter starts at 0x200 (=512)
        self.opcode = 0  # initial opcode
        self.I = 0  # index register
        self.sp = -1  # stack pointer
        self.draw_flag = 0
        self.keys = [0 for _ in range(16)]  # unsigned char

        # Clear registers V0-VF
        self.V = [0 for _ in range(16)] # register
        # Clear memory
        self.memory = [0 for _ in range(BUFFER_SIZE)]  # memory
        # Load fontset
        for i in range(0, len(CHIP8_FONTSET)):
            self.memory[i] = CHIP8_FONTSET[i]

        # Clear display
        self.disp_clear()
        # Clear stack
        self.stack = [0 for _ in range(16)]  # unsigned short

        # Reset timers
        self.delay_timer = 0
        self.sound_timer = 0

        if [c for c in self.V  if ((c < 0) or (c > 255)) ]:
            logger.error(f'Register over flow: {self.V}')

    def load_game(self, path_rom: str):
        logger.info(f'Loading ROM: {path_rom}')
        with open(path_rom, "rb") as f:
            i = 0
            while True:
                b = f.read(1) # read one hexadecimal and store as integer
                if b:
                    self.memory[i + 512] = int.from_bytes(b, 'big')
                else:
                    break
                i += 1

    def disp_clear(self):
        self.gfx = [0 for _ in range(WIDTH * HEIGHT)]

    def get_key(self):
        while True:
            key = keyboard.read_key()
            if  key in KEY_MAP:
                logger.info(f'[{key}] is pressed')
                return KEY_MAP[key]

    def draw(self, Vx, Vy, height):
        self.V[0xF] = 0
        logger.info(f'memory from I ({self.I}) to I + height ({self.I + height})')
        logger.info(f'memory: ({self.memory[self.I: self.I + height]})')
        logger.info(f'Vx, Vy = {Vx}, {Vy}')

        for y in range(0, height):
            pixel = self.memory[self.I + y]
            logger.info(f"raw {pixel} {bin(pixel)[2:].zfill(8).replace('0', '□').replace('1', '■')} at (x, y) = ({Vx}, {Vy + y})")
            for x in range(0, 8):

                if x > WIDTH - 1:
                    x -= WIDTH
                elif x < 0:
                    x += WIDTH
                if y > HEIGHT - 1:
                    y -= HEIGHT
                elif y < 0:
                    y += HEIGHT

                if ((pixel & (0x80 >> x)) != 0) & (Vx + x + ((Vy + y) * WIDTH) < 2048) :
                    if self.gfx[Vx + x + ((Vy + y) * WIDTH)] == 1:
                        logger.info('Pixel is changed to unset.')
                        self.V[0xF] = 1
                    self.gfx[Vx + x + ((Vy + y) * WIDTH)] ^= 1

        self.draw_flag = 1

    def set_keys(self):

        # Register callback for key
        for c in KEY_MAP:
            if keyboard.is_pressed(c):
                self.keys[KEY_MAP[c]] = 1
            else:
                self.keys[KEY_MAP[c]] = 0

    def sprite_add(self, Vx):
        return Vx * 5



    def emulate_cycle(self):
        """Proceed one cycle of emulater following the steps below:
        1. Fetch Opcode
        2. Decode Opcode
        3. Execute Opcode
        4. Update timers
        """
        logger.info(f'opcode: {hex(self.memory[self.pc])[2:]} {hex(self.memory[self.pc+1])[2:].zfill(2)} ')
        logger.info(f'V: {self.V}')
        logger.info(f'I: {self.I}')
        logger.info(f'pc: {self.pc}')
        logger.info(f'stack: {self.stack}')
        logger.info(f'keys: {self.keys}')
        logger.info(f'sp: {self.sp}')
        logger.info(f'delay_timer: {self.delay_timer}')

        # Fetch opcode
        self.opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
        self.pc += 2
        # Decode opcode
        if self.opcode & 0xFFFF == 0x00EE:
            logger.info("00EE: return from subroutine call")
            self.pc = self.stack[self.sp]
            self.sp -= 1
        elif self.opcode & 0xFFF0 == 0x00E0:
            logger.info("00E0: disp_clear()")
            self.disp_clear()
        elif self.opcode & 0xF000 == 0x0000:
            logger.info("0NNN: return;")
        elif self.opcode & 0xF000 == 0x1000:
            logger.info("# 1NNN: goto NNN;")
            self.pc =  self.opcode & 0x0FFF
        elif self.opcode & 0xF000 == 0x2000:
            NNN = self.opcode & 0x0FFF
            logger.info(f"# 2NNN: *(0xNNN)() Jump to subroutine at adress NNN ({NNN})")
            self.sp += 1
            self.stack[self.sp] = self.pc
            self.pc =  NNN
        elif self.opcode & 0xF000 == 0x3000:
            x = (self.opcode & 0x0F00) >> 8
            NN = self.opcode & 0x00FF
            if self.V[x] == NN:
                self.pc += 2
            logger.info(f"# 3XNN: if (Vx ({self.V[x]}) at x ({x}) == NN {NN})")
        elif self.opcode & 0xF000 == 0x4000:
            x = (self.opcode & 0x0F00) >> 8
            NN = self.opcode & 0x00FF
            logger.info(f"# 4XNN: if (Vx ({self.V[x]}) at x ({x}) != NN ({NN}))")
            if self.V[x] != NN:
                logger.info(f"    The condition holds. pc += 2")
                self.pc += 2
        elif self.opcode & 0xF000 == 0x5000:
            x = (self.opcode & 0x0F00) >> 8
            y = (self.opcode & 0x00F0) >> 4
            logger.info(f"#5XY0: if (Vx ({self.V[x]}) at x ({x}) == Vy ( ({self.V[y]}))) at y ({y})")
            if self.V[x] == self.V[y]:
                logger.info(f"    The condition holds. pc += 2")
                self.pc += 2
        elif self.opcode & 0xF000 == 0x6000:
            x = (self.opcode & 0x0F00) >> 8
            NN = self.opcode & 0x00FF
            logger.info(f"#6XNN: Sets VX ({self.V[x]}) at x ({x}) to NN ({NN})")
            self.V[x] = NN
        elif self.opcode & 0xF000 == 0x7000:
            x = (self.opcode & 0x0F00) >> 8
            NN = self.opcode & 0x00FF
            logger.info(f"#7XNN: Vx ({self.V[x]}) at x ({x}) += NN ({NN}) -> Vx ({self.V[x] + NN})")
            if self.V[x] > 255 - NN:
                self.V[x] -=  256 - NN # Carry flag is not changed
            else:
                self.V[x] += NN
            logger.info(f"#7XNN: Vx ({self.V[x]})")

        elif self.opcode & 0xF000 == 0x8000:
            x = (self.opcode & 0x0F00) >> 8
            y = (self.opcode & 0x00F0) >> 4
            case = self.opcode & 0x000F
            if case == 0:
                logger.info("#8XY0: Vx = Vy")
                self.V[x] = self.V[y]
            elif case == 1:
                logger.info("#8XY1: Vx |= Vy")
                self.V[x] |= self.V[y]
            elif case == 2:
                logger.info("#8XY2: Vx &= Vy")
                self.V[x] &= self.V[y]
            elif case == 3:
                logger.info("#8XY3: Vx ^= Vy")
                self.V[x] ^= self.V[y]
            elif case == 4:
                # 17 += 0 = 17
                # 16 += 255 -> 16
                if self.V[y] >  255 - self.V[x]:
                    logger.info(f"#8XY4: Vx ({self.V[x]}) at x ({x}) += Vy ({self.V[y]}) at y ({y}) -> Vx ({self.V[x] + self.V[y] - 255 }) with carry")
                    self.V[0xf] = 1 # carry
                    self.V[x] = self.V[x] + self.V[y] - 255 # TODO: avoid overflow
                else:
                    logger.info(f"#8XY4: Vx ({self.V[x]}) at x ({x}) += Vy ({self.V[y]}) at y ({y}) -> Vx ({self.V[x] + self.V[y]})")
                    self.V[0xf] = 0
                    self.V[x] += self.V[y]
                logger.info(f"#8XY4: Vx ({self.V[x]}))")

            elif case == 5:
                logger.info(f"#8XY5: Vx ({self.V[x]}) -= Vy ({self.V[y]}))")
                if self.V[x] <= self.V[y]:
                    logger.info(f"#8XY5: borrow from carry")
                    self.V[0xF] = 0
                    self.V[x] = 255 - (self.V[y] - self.V[x])
                else:
                    self.V[0xF] = 1
                    self.V[x] -= self.V[y]
                logger.info(f"#8XY5: Vx ({self.V[x]})")
            elif case == 6:
                logger.info(f"#8XY6: Vx ({self.V[x]}) at x ({x}) >>= 1")
                self.V[x] >>= 1
                logger.info(f"#8XY6: Vx ({self.V[x]}) at x ({x})")
            elif case == 7:
                logger.info(f"#8XY7: Vx ({self.V[x]}) at x ({x}) = Vy - Vx)")
                if self.V[x] <= self.V[y]:
                    self.V[x] = self.V[y] - self.V[x]  # no borrow
                    self.V[0xF] = 0
                else:
                    self.V[x] = 255 - self.V[x] + self.V[y]
                    self.V[0xF] = 1
                logger.info(f"#8XY7: Vx ({self.V[x]})")
            elif case == 0xE:
                logger.info(f"#8XYE: Vx ({self.V[x]}) at x ({x}) <<= 1")
                self.V[0xF] = int(bin(self.V[x])[2:].zfill(8)[0]) # the most significant bit to VF
                self.V[x] = int(bin(self.V[x] << 1)[2:].zfill(8)[1:], 2)
                logger.info(f"#8XYE: Vx ({self.V[x]}), V[0xF] ({self.V[0xF]})")
        elif self.opcode & 0xF000 == 0x9000:
            logger.info("#9XY0: if (Vx != Vy)")
            x = (self.opcode & 0x0F00) >> 8
            y = (self.opcode & 0x00F0) >> 4
            if self.V[x] != self.V[y]:
                    self.pc += 2
        elif self.opcode & 0xF000 == 0xA000:
            logger.info(f"#ANNN: I = NNN (sets I to the adress NNN ({self.opcode & 0x0FFF}))")
            self.I = self.opcode & 0x0FFF
        elif self.opcode & 0xF000 == 0xB000:
            logger.info("#BNNN: PC = V0 + NNN (jumps to the adress NNN plus V0)")
            self.pc = self.V[0] + self.opcode & 0x0FFF
        elif self.opcode & 0xF000 == 0xC000:
            logger.info("#CXNN: Vx = rand() & NN")
            x = (self.opcode & 0x0F00) >> 8
            NN = self.opcode & 0x00FF
            rnd = random.randint(0, 255)
            self.V[x] = rnd & NN

        elif self.opcode & 0xF000 == 0xD000:
            x = (self.opcode & 0x0F00) >> 8
            y = (self.opcode & 0x00F0) >> 4
            N = (self.opcode & 0x000F)
            logger.info(f"#DXYN: draw(Vx ({self.V[x]}) at x({x}), Vy ({self.V[y]}) at y ({y}), N height ({N}))")
            self.draw(self.V[x],self.V[y], N)
        elif self.opcode & 0xF0FF == 0xE09E:
            x = (self.opcode & 0x0F00) >> 8
            logger.info(f"#EX9E: if (key() ({self.keys[self.V[x]]}) ==  1 ~ Vx ({self.V[x]}) at x({x}))")
            if self.keys[self.V[x]] != 0:
                logger.info(f'key is pressed')
                self.pc += 2
        elif self.opcode & 0xF0FF == 0xE0A1:
            x = (self.opcode & 0x0F00) >> 8
            logger.info(f"#EXA1: if (key() ({self.keys[self.V[x]]}) != 1 ~ Vx ({self.V[x]}) at x({x}))")
            if self.keys[self.V[x]] == 0:
                logger.info(f'key is not pressed')
                self.pc += 2
        elif self.opcode & 0xF0FF == 0xF007:
            x = (self.opcode & 0x0F00) >> 8
            logger.info(f"#FX07: Vx ({self.V[x]}) at x({x})) = get_delay() ({self.delay_timer})")
            self.V[x] = self.delay_timer
        elif self.opcode & 0xF0FF == 0xF00A:
            x = (self.opcode & 0x0F00) >> 8
            logger.info(f"#FX0A: Vx ({self.V[x]}) at x({x})) = get_key() ({self.get_key()})")
            self.V[x] = self.get_key()
        elif self.opcode & 0xF0FF == 0xF015:
            logger.info("#FX15: delay_time(Vx)")
            x = (self.opcode & 0x0F00) >> 8
            self.delay_timer = self.V[x]
        elif self.opcode & 0xF0FF == 0xF018:
            logger.info("#FX18: sound_timer(Vx)")
            x = (self.opcode & 0x0F00) >> 8
            self.sound_timer = self.V[x]
        elif self.opcode & 0xF0FF == 0xF01E:
            x = (self.opcode & 0x0F00) >> 8
            logger.info(f"#FX1E: I ({self.I}) += Vx ({self.V[x]}) at x ({x})]")
            self.I += self.V[x]
            logger.info(f"#FX1E: I ({self.I})")
        elif self.opcode & 0xF0FF == 0xF029:
            x = (self.opcode & 0x0F00) >> 8
            logger.info(f"#FX29: I = sprite_addr[Vx] ({self.V[x]}) at x ({x})")
            self.I = self.V[x] * 5
            logger.info(f"#FX29: I ({self.I})")
        elif self.opcode & 0xF0FF == 0xF033:
            x = (self.opcode & 0x0F00) >> 8
            logger.info(f"#FX33: set_BCD(Vx) Vx ({self.V[x]}) at x ({x})")
                    # *(I+0) = BCD(3);
                    # *(I+1) = BCD(2);
                    # *(I+2) = BCD(1);
            bcd = str(self.V[x]).zfill(3)
            self.memory[self.I] = int(bcd[0])
            self.memory[self.I + 1] = int(bcd[1])
            self.memory[self.I + 2] = int(bcd[2])
        elif self.opcode & 0xF0FF == 0xF055:
            x = (self.opcode & 0x0F00) >> 8
            logger.info(f"#FX55: reg_dump(Vx ({self.V[x]}) at x ({x}), &I ({self.I}))")
            logger.info(f'V0 ~ VX: {self.V[:x]}')
            for i in range(x + 1):
                self.memory[self.I + i] = self.V[i]
        elif self.opcode & 0xF0FF == 0xF065:
            x = (self.opcode & 0x0F00) >> 8
            logger.info(f"#FX65: reg_load(Vx ({self.V[x]}) at x ({x}), &I ({self.I}))")
            for i in range(x + 1):
                self.V[i] = self.memory[self.I + i]
            logger.info(f'V0 ~ VX: {self.V[:x]}')
        else:
            raise('Unknown opcode: 0x%x\n' % self.opcode)

        # Update timers
        if (self.delay_timer > 0):
            self.delay_timer -= 1
        if (self.sound_timer > 0):
            if self.sound_timer == 1:
                logger.info('Beep!\n')
            self.sound_timer -= 1

