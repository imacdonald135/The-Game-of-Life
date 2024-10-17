import curses
import time

from bullet import Bullet

UP = '▲'
DOWN = '▼'
LEFT = '◀'
RIGHT = '▶'

class Player:
    def __init__(self, position, direction):
        self.position = position
        self.direction = direction
        self.avatar = UP
        self.last_fired = time.time()
        self.cooldown = 0.5
        self.radius = 2
        self.cooldown_level = 1
        self.radius_level = 1

    def move(self, stdscr, SIZE, bullets):
        key = stdscr.getch()  # Get the pressed key (non-blocking)
        max_x, max_y = stdscr.getmaxyx()

        # Handle movement
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
                (self.position[1] < max_y // 2 and max_y % 2 == 1) or (
                self.position[1] < max_y // 2 + 1) and max_y % 2 == 0):
            self.direction = "right"
            self.avatar = RIGHT
            self.position[1] += 1

        # Handle jumping
        elif key == ord(' '):  # Jump functionality
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

        # Handle firing bullets (with cooldown)
        if (time.time() - self.last_fired) > self.cooldown:
            if key == ord('w'):  # Fire upward
                bullet = Bullet(self.position.copy(), "up", self.radius)
                bullets.append(bullet)
                self.last_fired = time.time()  # Reset cooldown timer

            elif key == ord('a'):  # Fire left
                bullet = Bullet(self.position.copy(), "left", self.radius)
                bullets.append(bullet)
                self.last_fired = time.time()

            elif key == ord('d'):  # Fire right
                bullet = Bullet(self.position.copy(), "right", self.radius)
                bullets.append(bullet)
                self.last_fired = time.time()

            elif key == ord('s'):  # Fire downward
                bullet = Bullet(self.position.copy(), "down", self.radius)
                bullets.append(bullet)
                self.last_fired = time.time()

    def get_bullet(self, stdscr):

        key = stdscr.getch()

        if key == ord("b"):
            return Bullet(self.position, self.direction)
        return None

    def decrease_cooldown(self):
        self.cooldown = self.cooldown * 0.66
        self.cooldown_level += 1

    def increase_radius(self):
        self.radius = self.radius + 2
        self.radius_level += 1

    def increase_cooldown(self):

        if self.cooldown_level > 1:
            self.cooldown = self.cooldown / 0.66
            self.cooldown_level -= 1

    def decrease_radius(self):
        if self.radius_level > 1:
            self.radius = self.radius - 2
            self.radius_level -= 1