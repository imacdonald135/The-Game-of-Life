import time
import numpy as np
import curses  # For handling keyboard input and screen control
import random


def initlise_matrix(SIZE):
    """Initializes the matrix with random 0s and 1s."""
    matrix = np.zeros(SIZE)
    x = random.randint(10, SIZE[0] - 10)
    y = random.randint(10, SIZE[1] - 10)

    for i in range(x, x + 10):
        for j in range(y, y + 10):
            matrix[i, j] = random.randint(0, 1)
    return matrix


def print_matrix(stdscr, matrix, player_pos):
    """Prints the matrix to the screen with player position marked as 'X'."""
    # Clear the screen
    stdscr.clear()
    died = False
    for i, row in enumerate(matrix):
        row_to_print = []
        for j, elem in enumerate(row):
            # Draw the player character if it's the player's position, otherwise the normal cell
            if matrix[i, j] == 1 and (i, j) == player_pos:
                row_to_print.append("X")
                died = True
            elif (i, j) == player_pos:
                row_to_print.append("X")
            else:
                row_to_print.append("#" if elem == 1 else " ")
        try:
            if i == 0:
                stdscr.addstr(i, 0, f"{stdscr.getmaxyx()}      {player_pos}")
            else:
                stdscr.addstr(i, 0, " ".join(row_to_print))  # Print each row
        except curses.error:
            # Handle the error when trying to print outside the screen bounds
            break  # Exit the loop if we cannot print more rows

    stdscr.refresh()  # Refresh the screen
    return died


def print_death_screen(stdscr, matrix, player_pos):
    """ Flash the player icon to show the death """
    for n in range(6):
        for i, row in enumerate(matrix):
            row_to_print = []
            for j, elem in enumerate(row):
                # Draw the player character if it's the player's position, otherwise the normal cell
                if (i, j) == player_pos and n % 2 == 0:
                    row_to_print.append("X")


                elif (i, j) == player_pos:
                    row_to_print.append(" ")

                else:
                    row_to_print.append("#" if elem == 1 else " ")
            try:
                if i == 0:
                    stdscr.addstr(i, 0, f"{stdscr.getmaxyx()}      {player_pos}")
                else:
                    stdscr.addstr(i, 0, " ".join(row_to_print))  # Print each row
            except curses.error:
                # Handle the error when trying to print outside the screen bounds
                break  # Exit the loop if we cannot print more rows

            stdscr.refresh()  # Refresh the screen

        time.sleep(0.33)


def next_iteration(matrix, SIZE, player_pos):
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
        px, py = player_pos

        bad_x = True
        bad_y = True

        while (bad_y or bad_x):
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


def handle_player_movement(stdscr, player_pos, SIZE):
    """Handles player movement based on arrow key input."""
    key = stdscr.getch()  # Get the pressed key (non-blocking)

    x, y = player_pos
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


import time  # Import time module to track the elapsed time


def main(stdscr):
    # Initialize the curses window
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.keypad(True)  # Enable arrow key input
    stdscr.timeout(0)  # No timeout, so we can handle key presses immediately
    start_screen = True

    def reset_game():
        SIZE = stdscr.getmaxyx()  # Fixed grid size for now, but you can adjust this if needed
        SIZE = (SIZE[0], SIZE[1] // 2)
        matrix = initlise_matrix(SIZE)
        player_pos = (5, 5)  # Start player in the middle of the grid
        return SIZE, matrix, player_pos

    # Outer loop that allows resetting the game
    while True:
        SIZE, matrix, player_pos = reset_game()

        start_time = time.time()  # Record the start time when the game begins

        try:
            count = 0
            game_playing = True
            player_alive = True
            last_frame_matrix = matrix
            last_player_pos = player_pos
            seconds = 0
            game_mode = "Easy"
            refresh_rate = 0.01

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
                    refresh_rate = 0.5
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
                player_alive = not print_matrix(stdscr, matrix, player_pos)

                if not player_alive:
                    print_death_screen(stdscr, matrix, player_pos)
                    # Store the last frame and player position before breaking the loop
                    last_frame_matrix = matrix
                    last_player_pos = player_pos
                    break

                # Display the elapsed time at the top of the screen
                stdscr.addstr(0, 0, f"Time: {seconds} seconds")

                # Handle player movement
                player_pos = handle_player_movement(stdscr, player_pos, SIZE)

                if count == 2:
                    # Update the Game of Life matrix
                    matrix = next_iteration(matrix, SIZE, player_pos)
                    count = 0
                else:
                    count += 1

                time.sleep(refresh_rate)  # Small delay to control the speed of the game

            # Game over logic
            while not player_alive:
                # Draw the last frame of the game
                # print_matrix(stdscr, last_frame_matrix, last_player_pos)

                stdscr.clear()

                # Overlay the "Game Over" message
                stdscr.addstr(SIZE[0] // 2 - 1, SIZE[1] // 2 - 5, "GAME OVER!")
                stdscr.addstr(SIZE[0] // 2 + 1, SIZE[1] // 2 - 5, "Press 'r' to reset, 's' to go back to the start screen, or 'q' to quit")
                stdscr.addstr(SIZE[0] // 2 + 3, SIZE[1] // 2 - 5, f"Your score was {seconds}!")
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
                    break
                time.sleep(0.05)

        except KeyboardInterrupt:
            pass  # Handle Ctrl+C gracefully


# Wrapper to run the curses-based main loop
curses.wrapper(main)
