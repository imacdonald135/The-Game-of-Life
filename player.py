import curses


UP = '▲'
DOWN = '▼'
LEFT = '◀'
RIGHT = '▶'

class Player:
    def __init__(self, position, direction):
        self.position = position
        self.direction = direction
        self.avatar = UP

    def move(self, stdscr, SIZE):
        key = stdscr.getch()  # Get the pressed key (non-blocking)
        max_x, max_y = stdscr.getmaxyx()
        if key == curses.KEY_UP and self.position[0] > 0:
            self.direction = "up"
            self.avatar = UP
            self.position[0] -= 1
        elif key == curses.KEY_DOWN and self.position[0] < SIZE[0] - 1 and self.position[0] < max_x - 1:
            self.direction = "down"
            self.avatar = DOWN
            self.position[0] += 1
        elif key == curses.KEY_LEFT and self.position[1] > 0:
            self.direction = "left"
            self.avatar = LEFT
            self.position[1] -= 1
        elif key == curses.KEY_RIGHT and self.position[1] < SIZE[1] - 1 and (
                (self.position[1] < max_y // 2 and max_y % 2 == 1) or (self.position[1] < max_y // 2 + 1) and max_y % 2 == 0):
            self.direction = "right"
            self.avatar = RIGHT
            self.position[1] += 1

        elif key == ord(' '):
            if self.direction == "up" and self.position[0] > 2:
                self.position[0] -= 3
            elif self.direction == "down" and self.position[0] < SIZE[0] - 3 and self.position[0] < max_x - 3:
                self.position[0] += 3
            elif self.direction == "left" and self.position[1] > 2:
                self.position[1] -= 3
            elif self.direction == "right" and self.position[1] < SIZE[1] - 3 and (
                    (self.position[1] < max_y // 2 - 2 and max_y % 2 == 1) or (
                    self.position[1] < max_y // 2 - 1) and max_y % 2 == 0):
                self.position[1] += 3

