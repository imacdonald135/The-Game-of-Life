import time
import numpy as np
import curses  # For handling keyboard input and screen control
import random
import math

from bullet import Bullet
from player import Player
from snitch import Snitch


def initialize_colors():
    """Initialize custom colors and color pairs."""
    curses.start_color()  # Initialize color support

    # Custom colors
    curses.init_color(10, 800, 50, 50)  # Bright blue
    curses.init_color(11, 250, 40, 40)  # Bright red

    # Define color pairs
    curses.init_pair(1, 11, curses.COLOR_BLACK)  # Custom bright red for player
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Default green
    curses.init_pair(3, 10, curses.COLOR_BLACK)  # Custom bright blue


def initlise_matrix(SIZE):
    """Initializes the matrix with random 0s and 1s."""
    matrix = np.zeros(SIZE)
    x = random.randint(10, SIZE[0] - 10)
    y = random.randint(10, SIZE[1] - 10)

    for i in range(x, x + 10):
        for j in range(y, y + 10):
            matrix[i, j] = random.randint(0, 1)
    return matrix

def print_matrix(stdscr, matrix, player):
    """Prints the matrix to the screen with player position marked as 'X' in red."""
    # Start colors in curses# Example: green for other elements if needed

    # Clear the screen
    stdscr.clear()
    died = False
    hit_snitch = matrix[player.position[0], player.position[1]] == 2

    for i, row in enumerate(matrix):
        row_to_print = []
        for j, elem in enumerate(row):
            # Check if it's the player's position
            if [i, j] == player.position:
                if matrix[i, j] == 1:  # If player is on a dangerous cell
                    died = True
                row_to_print.append((player.avatar, curses.color_pair(2)))# Green 'X' for player
            else:
                row_to_print.append(
                    ("#", curses.color_pair(1)) if elem == 1 else
                    ("@", curses.A_NORMAL) if elem == 2 else
                    ("o", curses.A_NORMAL) if elem == 3 else
                    (" ", curses.A_NORMAL)
                )

        try:
            # Print the row, applying color only to the player's 'X'
            for index, (char, style) in enumerate(row_to_print):
                stdscr.addstr(i, index * 2, char, style)  # Use style for each character
        except curses.error:
            # Handle the error when trying to print outside the screen bounds
            break  # Exit the loop if we cannot print more rows

    stdscr.refresh()  # Refresh the screen
    return died, hit_snitch



def print_death_screen(stdscr, matrix, player):
    """ Flash the player icon to show the death """


    for n in range(6):
        for i, row in enumerate(matrix):
            row_to_print = []
            for j, elem in enumerate(row):
                # Flash the player icon (alternates between 'X' and ' ')
                if [i, j] == player.position:
                    if n % 2 == 0:  # Show the player icon ('X')
                        row_to_print.append((player.avatar, curses.color_pair(3)))  # Use default red 'X' for player
                    else:  # Hide the player icon (' ')
                        row_to_print.append((" ", curses.A_NORMAL))
                else:
                    # Use the same color scheme as in print_matrix
                    if elem == 1:
                        row_to_print.append(("#", curses.color_pair(1)))  # Default green for other elements
                    else:
                        row_to_print.append((" ", curses.A_NORMAL))  # Space for empty cells

            try:
                # Print the row, applying styles to flash player icon
                for index, (char, style) in enumerate(row_to_print):
                    stdscr.addstr(i, index * 2, char, style)  # Use style for each character
            except curses.error:
                break  # Exit the loop if we cannot print more rows

        stdscr.refresh()  # Refresh the screen after each frame
        time.sleep(0.33)  # Delay between frames



def next_iteration(matrix, SIZE, player):
    """Computes the next state of the matrix based on the rules of Conway's Game of Life."""
    next_matrix = np.zeros(SIZE)

    for i in range(SIZE[0]):
        for j in range(SIZE[1]):
            alive_neighbours = 0
            for n in range(i - 1, i + 2):
                for m in range(j - 1, j + 2):
                    if n >= 0 and n < SIZE[0] and m >= 0 and m < SIZE[1] and not (i == n and j == m):
                        if matrix[n, m] == 1:
                            alive_neighbours += 1
            if (matrix[i, j] == 1 and (alive_neighbours == 2 or alive_neighbours == 3)) or (
                    matrix[i, j] == 0 and alive_neighbours == 3):
                next_matrix[i, j] = 1
            else:
                next_matrix[i, j] = 0

    if 1 == random.randint(0, 5):
        px, py = player.position[0], player.position[1]
        min_distance = 10  # Minimum distance from the player

        valid_position = False

        while not valid_position:
            # Random x and y for the top-left corner of the 10x10 block
            x = random.randint(2, SIZE[0] - 12)
            y = random.randint(2, SIZE[1] - 12)

            # Calculate the center of the 10x10 block
            block_center_x = x + 5
            block_center_y = y + 5

            # Compute the distance from the player to the block center
            distance = math.sqrt((block_center_x - px) ** 2 + (block_center_y - py) ** 2)

            # Check if the distance is greater than or equal to the minimum distance
            if distance >= min_distance:
                valid_position = True

        # Create the 10x10 random block at the valid position
        for i in range(x, min(x + 10, SIZE[0])):
            for j in range(y, min(y + 10, SIZE[1])):
                next_matrix[i, j] = random.randint(0, 1)

    return next_matrix

def update_bullets(bullets, stdscr, SIZE):

    for bullet in bullets:
        bullet.update(stdscr, SIZE)

    bullets[:] = [bullet for bullet in bullets if not bullet.dead]



def main(stdscr):
    # Initialize the curses window
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.keypad(True)  # Enable arrow key input
    stdscr.timeout(0)  # No timeout, so we can handle key presses immediately
    initialize_colors()
    start_screen = True
    count = 0
    game_playing = False
    player_dead = False
    score = 0
    total_score = 0
    game_mode = "Easy"
    refresh_rate = 0.04
    coins = 0
    radius_selected = True
    cooldown_selected = False
    store_screen = False
    bullets = []
    player = Player([5,5], "up")

    def reset_game():
        SIZE = stdscr.getmaxyx()  # Fixed grid size for now, but you can adjust this if needed
        SIZE = (SIZE[0], SIZE[1] // 2)
        matrix = initlise_matrix(SIZE)

        snitch = Snitch([10,10])
        snitch.reset(stdscr)
        matrix[snitch.position[0], snitch.position[1]] = 2
        return SIZE, matrix, snitch, 0


    # Outer loop that allows resetting the game
    while True:

        SIZE, matrix, snitch, score = reset_game()

        start_time = time.time()  # Record the start time when the game begins
        last_hit_snitch = time.time()
        try:

            while start_screen:

                stdscr.clear()

                # Overlay the "Game Over" message
                stdscr.addstr(SIZE[0] // 2 - 3, SIZE[1] // 2 - 5, "Welcome to THE GAME OF LIFE (conway edition)!")
                stdscr.addstr(SIZE[0] // 2 - 1, SIZE[1] // 2 - 5, "Press 'e' to play easy mode or 'h' to for hard mode")
                stdscr.addstr(SIZE[0] // 2 + 1, SIZE[1] // 2 - 5, "Press 's' to go to store / character setup")
                stdscr.addstr(SIZE[0] // 2 + 3, SIZE[1] // 2 - 5, f"You have selected game mode: {game_mode}")
                stdscr.addstr(SIZE[0] // 2 + 5, SIZE[1] // 2 - 5, f"Press ENTER to start !")


                # Wait for the player's input
                key = stdscr.getch()

                if key == ord('e'):
                    game_mode = "Easy"
                    refresh_rate = 0.04
                    stdscr.refresh()
                elif key == ord('h'):
                    game_mode = "Hard"
                    refresh_rate = 0.02
                    stdscr.refresh()
                elif key == ord('s'):
                    start_screen = False
                    store_screen = True
                elif key == curses.KEY_ENTER or key in [10, 13]:
                    # Start the game
                    start_screen = False
                    game_playing = True  # Restart the game loop by breaking the inner "Game Over" loop
                    break
                time.sleep(0.05)

            while store_screen:
                stdscr.clear()
                # Overlay the "Game Over" message and store options
                stdscr.addstr(SIZE[0] // 2 - 10, SIZE[1] // 3, "Welcome to the store!")
                stdscr.addstr(SIZE[0] // 2 - 10, int(SIZE[1] + SIZE[1] // 2), f"Coins: {coins}")

                # Display the selection pointer
                if radius_selected:
                    stdscr.addstr(SIZE[0] // 2 - 1, int(SIZE[1] / 2) - 2, "|")
                else:
                    stdscr.addstr(SIZE[0] // 2 - 1, int(SIZE[1] / 2) - 2, " ")

                if cooldown_selected:
                    stdscr.addstr(SIZE[0] // 2 + 1, int(SIZE[1] / 2) - 2, "|")
                else:
                    stdscr.addstr(SIZE[0] // 2 + 1, int(SIZE[1] / 2) - 2, " ")

                stdscr.addstr(SIZE[0] // 2 - 1, int(SIZE[1] / 2), f"Radius level: {player.radius_level}")
                stdscr.addstr(SIZE[0] // 2 + 1, int(SIZE[1] / 2), f"Cooldown level: {player.cooldown_level}")

                stdscr.addstr(SIZE[0] // 2 + 10, SIZE[1] // 3, "Press 'r' to return to the start screen")

                # Wait for the player's input
                key = stdscr.getch()

                # Handle input for toggling between options
                if key == curses.KEY_UP:
                    radius_selected = True
                    cooldown_selected = False
                elif key == curses.KEY_DOWN:
                    radius_selected = False
                    cooldown_selected = True

                elif key == curses.KEY_RIGHT:
                    if coins > 0:
                        if radius_selected:
                            player.increase_radius()
                        else:
                            player.decrease_cooldown()
                        coins -= 1;

                elif key == curses.KEY_LEFT:

                    if radius_selected:
                        level_before = player.radius_level
                        player.decrease_radius()
                        level_after = player.radius_level
                        if level_before != level_after:
                            coins += 1
                    else:
                        level_before = player.cooldown_level
                        player.increase_radius()
                        level_after = player.cooldown_level
                        if level_before != level_after:
                            coins += 1
                elif key == ord("p"):
                    coins += 10
                # Press 'r' to return to the start screen
                if key == ord("r"):
                    start_screen = True
                    store_screen = False
                    break
                time.sleep(0.01)
                stdscr.refresh()

            while game_playing:
                # Calculate the elapsed time in seconds
                current_time = time.time()
                seconds = int(current_time - start_time)  # Calculate elapsed seconds

                # Print the game matrix with player position
                player_dead, hit_snitch = print_matrix(stdscr, matrix, player)
                if hit_snitch:
                    if time.time() - 0.5 > last_hit_snitch:
                        score += 1
                        total_score += 1
                        if total_score % 5 == 0:
                            coins += 1
                        snitch.reset(stdscr)
                        last_hit_snitch = time.time()

                if player_dead:
                    print_death_screen(stdscr, matrix, player)
                    break

                # Display the elapsed time and score
                stdscr.addstr(0, 0, f"Score: {score}")

                # Handle player movement
                player.move(stdscr, SIZE, bullets)

                # Update the bullets
                update_bullets(bullets, stdscr, SIZE)

                if count == 2:
                    # Update the Game of Life matrix
                    matrix = next_iteration(matrix, SIZE, player)
                    matrix[snitch.position[0], snitch.position[1]] = 2
                    # Place bullets in the matrix
                    for bullet in bullets:
                        # Check the neighboring cells around the bullet's position
                        bullet_x, bullet_y = bullet.position[0], bullet.position[1]

                        # Define neighbor positions (8 possible directions)
                        neighbors = [
                            (bullet_x - 1, bullet_y),  # Up
                            (bullet_x + 1, bullet_y),  # Down
                            (bullet_x, bullet_y - 1),  # Left
                            (bullet_x, bullet_y + 1),  # Right
                            (bullet_x - 1, bullet_y - 1),  # Top-left
                            (bullet_x - 1, bullet_y + 1),  # Top-right
                            (bullet_x + 1, bullet_y - 1),  # Bottom-left
                            (bullet_x + 1, bullet_y + 1)  # Bottom-right
                        ]

                        # Check if any neighbor has a `1` (dangerous cell)
                        if any(0 <= x < len(matrix) and 0 <= y < len(matrix[0]) and matrix[x][y] == 1 for x, y in
                               neighbors):
                            bullet.dead = True
                            # Remove surrounding `1`s in a 10x10 area around the bullet
                            for x in range(max(0, bullet.position[0] - bullet.radius),
                                           min(len(matrix) - 1, bullet.position[0] + bullet.radius + 1)):
                                for y in range(max(0, bullet.position[1] - bullet.radius),
                                               min(len(matrix[0]) - 1, bullet.position[1] + bullet.radius + 1)):
                                    if matrix[x][y] == 1:
                                        matrix[x, y] = 0
                        else:
                            # If no neighboring `1` is found, continue placing the bullet in the matrix
                            matrix[bullet.position[0], bullet.position[1]] = 3

                    count = 0
                else:
                    count += 1

                time.sleep(refresh_rate)

            # Game over logic
            while player_dead:

                stdscr.clear()

                # Overlay the "Game Over" message
                stdscr.addstr(SIZE[0] // 2 - 1, SIZE[1] // 2 - 5, "GAME OVER!")
                stdscr.addstr(SIZE[0] // 2 + 1, SIZE[1] // 2 - 5, "Press 'r' to reset, 's' to go back to the start screen, or 'q' to quit")
                stdscr.addstr(SIZE[0] // 2 + 3, SIZE[1] // 2 - 5, f"Your score was {score}!")
                stdscr.refresh()

                # Wait for the player's input
                key = stdscr.getch()
                if key == ord('q'):
                    # Quit the game
                    stdscr.addstr(SIZE[0] // 2 - 3, SIZE[1] // 2 - 5, "q pressed")
                    return  # Exit the outer loop and end the game
                elif key == ord('s'):
                    start_screen = True
                    break
                elif key == ord('r'):
                    # Reset the game
                    start_screen = False
                    game_playing = True
                    store_screen = False
                    score = 0
                    break
                time.sleep(0.05)
        except KeyboardInterrupt:
            return  # Handle Ctrl+C gracefully


# Wrapper to run the curses-based main loop
curses.wrapper(main)
