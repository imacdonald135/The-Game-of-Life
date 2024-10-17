import time
import numpy as np
import curses  # For handling keyboard input and screen control
import random
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

        bad_x = True
        bad_y = True

        while bad_y or bad_x:
            x = random.randint(0, SIZE[0] - 10)
            y = random.randint(0, SIZE[1] - 10)

            if px in range(x - 5, x + 15):
                x = random.randint(0, SIZE[0] - 10)
                bad_x = False
            if py in range(y - 5, y + 15):
                y = random.randint(0, SIZE[1] - 10)
                bad_y = False

        for i in range(x, x + 10):
            for j in range(y, y + 10):
                next_matrix[i, j] = random.randint(0, 1)

    return next_matrix


import time  # Import time module to track the elapsed time

def main(stdscr):
    # Initialize the curses window
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.keypad(True)  # Enable arrow key input
    stdscr.timeout(0)  # No timeout, so we can handle key presses immediately
    initialize_colors()
    start_screen = True

    def reset_game():
        SIZE = stdscr.getmaxyx()  # Fixed grid size for now, but you can adjust this if needed
        SIZE = (SIZE[0], SIZE[1] // 2)
        matrix = initlise_matrix(SIZE)
        player = Player([5, 5], "up")
        snitch = Snitch([10,10])
        snitch.reset(stdscr)
        matrix[snitch.position[0], snitch.position[1]] = 2
        return SIZE, matrix, player, snitch

    # Outer loop that allows resetting the game
    while True:
        SIZE, matrix, player, snitch = reset_game()

        start_time = time.time()  # Record the start time when the game begins

        try:
            count = 0
            game_playing = True
            player_alive = True
            score = 0
            game_mode = "Easy"
            refresh_rate = 0.02


            while start_screen:

                stdscr.clear()

                # Overlay the "Game Over" message
                stdscr.addstr(SIZE[0] // 2 - 1, SIZE[1] // 2 - 5, "Welcome to THE GAME OF LIFE (conway edition)!")
                stdscr.addstr(SIZE[0] // 2 + 1, SIZE[1] // 2 - 5, "Press 'e' to play easy mode or 'h' to for hard mode")
                stdscr.addstr(SIZE[0] // 2 + 3, SIZE[1] // 2 - 5, f"You have selected game mode: {game_mode}")
                stdscr.addstr(SIZE[0] // 2 + 5, SIZE[1] // 2 - 5, f"Press 's' to start !")


                # Wait for the player's input
                key = stdscr.getch()

                if key == ord('e'):
                    game_mode = "Easy"
                    refresh_rate = 0.1
                    stdscr.refresh()
                elif key == ord('h'):
                    game_mode = "Hard"
                    refresh_rate = 0.05
                    stdscr.refresh()
                elif key == ord('s'):
                    # Start the game
                    start_screen = False
                    game_playing = True  # Restart the game loop by breaking the inner "Game Over" loop
                    break
                time.sleep(0.05)

            while game_playing:
                # Calculate the elapsed time in seconds
                current_time = time.time()
                seconds = int(current_time - start_time)  # Calculate elapsed seconds

                # Print the game matrix with player position
                player_dead, hit_snitch = print_matrix(stdscr, matrix, player)
                if hit_snitch:
                    score += 1
                    snitch.reset(stdscr)

                if player_dead:
                    print_death_screen(stdscr, matrix, player)
                    break

                # Display the elapsed time at the top of the screen
                stdscr.addstr(0, 0, f"Score: {score}")

                # Handle player movement
                player.move(stdscr, SIZE)

                if count == 2:
                    # Update the Game of Life matrix
                    matrix = next_iteration(matrix, SIZE, player)
                    matrix[snitch.position[0], snitch.position[1]] = 2
                    count = 0
                else:
                    count += 1

                time.sleep(refresh_rate)  # Small delay to control the speed of the game

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
                    return  # Exit the outer loop and end the game
                elif key == ord('s'):
                    start_screen = True
                    break
                elif key == ord('r'):
                    # Reset the game
                    start_screen = False
                    game_playing = True  # Restart the game loop by breaking the inner "Game Over" loop
                    score = 0
                    break
                time.sleep(0.05)

        except KeyboardInterrupt:
            pass  # Handle Ctrl+C gracefully


# Wrapper to run the curses-based main loop
curses.wrapper(main)
