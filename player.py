import curses

class Player:
    def __init__(self, position, direction):
        self.position = position
        self.direction = direction

    def move(self, stdscr):
        key = stdscr.getch()  # Get the pressed key (non-blocking)
        max_x, max_y = stdscr.getmaxyx()
        if key == curses.KEY_UP and x > 0:
            x -= 1
        elif key == curses.KEY_DOWN and x < SIZE[0] - 1 and x < max_x - 1:
            x += 1
        elif key == curses.KEY_LEFT and y > 0:
            y -= 1
        elif key == curses.KEY_RIGHT and y < SIZE[1] - 1 and (
                (y < max_y // 2 and max_y % 2 == 1) or (y < max_y // 2 + 1) and max_y % 2 == 0):
            y += 1

        return (x, y)