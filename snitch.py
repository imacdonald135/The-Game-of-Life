import random

class Snitch:

    def __init__(self, position):
        self.position = position


    def reset(self, stdscr):
        SIZE = stdscr.getmaxyx()  # Fixed grid size for now, but you can adjust this if needed
        SIZE = (SIZE[0], SIZE[1] // 2)
        self.position = (random.randint(3, SIZE[0] - 3), random.randint(3, SIZE[1]) - 3)