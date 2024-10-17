class Bullet:

    def __init__(self, position, direction, radius):
        self.position = position
        self.direction = direction
        self.dead = False
        self.radius = radius

        if direction == "up" or direction == "down":
            self.avatar = '|'
        else:
            self.avatar = '—'

    def update(self, stdscr, SIZE):

        max_x, max_y = stdscr.getmaxyx()
        if self.direction == "up" and self.position[0] > 0:
            self.position[0] -= 1
        elif self.direction == "down" and self.position[0] < SIZE[0] - 1 and self.position[0] < max_x - 1:
            self.position[0] += 1
        elif self.direction == "left" and self.position[1] > 0:
            self.position[1] -= 1
        elif self.direction == "right" and self.position[1] < SIZE[1] - 1 and (
                (self.position[1] < max_y // 2 and max_y % 2 == 1) or (
                self.position[1] < max_y // 2 + 1) and max_y % 2 == 0):
            self.position[1] += 1
        else:
            self.dead = True