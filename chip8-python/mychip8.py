


class MyChip8(object):

    draw_flag = 0
    def __init__(self):
        """Initialize registers and memory once
        """
        pass

    def load_game(self, game_name:str):
        pass

    def set_keys(self):
        pass

    def emulate_cycle(self):
        """Proceed one cycle of emulater following the steps below:
        1. Fetch Opcode
        2. Decode Opcode
        3. Execute Opcode
        4. Update timers 
        """
