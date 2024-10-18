import time
import numpy as np
import curses  # For handling keyboard input and screen control
import random
import math
import sqlite3
import os

from enum import Enum
from sympy import false

from bullet import Bullet
from player import Player
from snitch import Snitch
from welcometext import WelcomeText

MATRIX_ITERATION_TICKS = 0
EGG_PLACED = False
EGG_COORDS = None

class GameState(Enum):
    START_SCREEN = 1
    STORE_SCREEN = 2
    GAME_PLAYING = 3
    PLAYER_DEAD = 4
    JUST_WATCHING = 5
    ROUND_END = 6

def initialize_colors():
    """Initialize custom colors and color pairs."""
    curses.start_color()  # Initialize color support

    # Custom colors
    curses.init_color(10, 800, 50, 50)
    curses.init_color(11, 1000, 333, 333)
    curses.init_color(12, 800, 800, 100)
    curses.init_color(13, 800, 400, 100)
    curses.init_color(14, 600, 200, 50)
    curses.init_color(15, 1000, 1000, 200)
    curses.init_color(16, 1000, 500, 100)
    curses.init_color(17, 1000, 100, 50)



    # Define color pairs
    curses.init_pair(1, 11, curses.COLOR_BLACK)  # Custom bright red for player
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Default green
    curses.init_pair(3, 10, curses.COLOR_BLACK)  # Custom bright blue
    curses.init_pair(4, 12, curses.COLOR_BLACK)  # Custom bright blue
    curses.init_pair(5, 13, curses.COLOR_BLACK)  # Custom bright blue
    curses.init_pair(6, 14, curses.COLOR_BLACK)  # Custom bright blue
    curses.init_pair(7, 15, curses.COLOR_BLACK)  # Custom bright blue
    curses.init_pair(8, 16, curses.COLOR_BLACK)  # Custom bright blue
    curses.init_pair(9, 17, curses.COLOR_BLACK)  # Custom bright blue


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
                    ("O", curses.A_NORMAL) if elem == 4 else
                    (" ", curses.A_NORMAL) if elem == 5 else
                    ("O", curses.A_NORMAL) if elem == 6 else
                    ("3", curses.color_pair(7)) if elem == 7 else
                    ("2", curses.color_pair(8)) if elem == 8 else
                    ("1", curses.color_pair(9)) if elem == 9 else
                    (" ", curses.A_NORMAL)
                )
                if matrix[i][j] == 4:
                    matrix[i][j] = 5
                elif matrix[i][j] == 5:
                    matrix[i][j] = 6
                elif matrix[i][j] == 6:
                    matrix[i][j] = 0

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
    global MATRIX_ITERATION_TICKS, EGG_COORDS, EGG_PLACED
    for i in range(SIZE[0]):
        for j in range(SIZE[1]):
            alive_neighbours = 0
            for n in range(i - 1, i + 2):
                for m in range(j - 1, j + 2):
                    if n >= 0 and n < SIZE[0] and m >= 0 and m < SIZE[1] and not (i == n and j == m):
                        if matrix[n, m] == 1:
                            alive_neighbours += 1
            if (matrix[i, j] == 1 and (alive_neighbours == 3 or alive_neighbours == 2)) or (
                    matrix[i, j] == 0 and alive_neighbours == 3):
                next_matrix[i, j] = 1
            else:
                next_matrix[i, j] = 0

    if not EGG_PLACED:
        if 1 == random.randint(0, 5):
            px, py = player.position[0], player.position[1]
            min_distance = 10  # Minimum distance from the player

            valid_position = False
            block_center_x = None
            block_center_y = None

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

            EGG_COORDS = [block_center_x, block_center_y]
            next_matrix[EGG_COORDS[0], EGG_COORDS[1]] = 7
            EGG_PLACED = True
    else:
        MATRIX_ITERATION_TICKS += 1
        next_matrix[EGG_COORDS[0], EGG_COORDS[1]] = 7 + MATRIX_ITERATION_TICKS//5
        # Create the 10x10 random block at the valid position
    if MATRIX_ITERATION_TICKS >= 15:

        # for i in range(max(EGG_COORDS[0] -5, 0), min(EGG_COORDS[0] + 6, SIZE[0])):
        #     for j in range(max(0, EGG_COORDS[1] - 5), min(EGG_COORDS[1]+6, SIZE[1])):
        #         next_matrix[i, j] = random.randint(0, 1)
        x = EGG_COORDS[0]
        y = EGG_COORDS[1]

        if 1 == random.randint(0, 1):
            next_matrix[x - 1][y - 2] = 1
            next_matrix[x][y] = 1
            next_matrix[x + 1][y - 3] = 1
            next_matrix[x + 1][y - 2] = 1
            next_matrix[x + 1][y + 1] = 1
            next_matrix[x + 1][y + 2] = 1
            next_matrix[x + 1][y + 3] = 1
        else:
            next_matrix[x - 1][y] = 1
            next_matrix[x - 1][y + 1] = 1
            next_matrix[x][y - 1] = 1
            next_matrix[x][y] = 1
            next_matrix[x+1][y] = 1



        MATRIX_ITERATION_TICKS = 0
        EGG_COORDS = None
        EGG_PLACED = False

    return next_matrix

def update_bullets(bullets, stdscr, SIZE):

    for bullet in bullets:
        bullet.update(stdscr, SIZE)

    bullets[:] = [bullet for bullet in bullets if not bullet.dead]

def connect_to_database(db_name='game_data.db'):
    # Check if the database file exists
    db_exists = os.path.exists(db_name)

    # Connect to the database (it will be created if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create the player_data table if the database is newly created
    if not db_exists:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            high_score INTEGER,
            character_level INTEGER
        )
        ''')

    # Commit changes and return the connection and cursor
    conn.commit()
    return conn, cursor

def get_player_data(cursor):
    cursor.execute('SELECT player_name, high_score, character_level FROM player_data LIMIT 1')
    return cursor.fetchone()

def create_new_player(cursor, player_name='Player1'):
    cursor.execute('''
    INSERT INTO player_data (player_name, high_score, character_level) 
    VALUES (?, ?, ?)''', (player_name, 0, 1))  # Starting with a score of 0 and level 1
    cursor.connection.commit()  # Commit the changes

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
    round_num = 1
    score = 0
    total_score = 0
    game_mode = "Easy"
    refresh_rate = 0.04
    coins = 0
    radius_selected = True
    cooldown_selected = False
    store_screen = False
    game_state = GameState.START_SCREEN
    bullets = []
    conn, cursor = connect_to_database()
    player_data = get_player_data(cursor)
    if player_data is None:
        # No player exists, create a new one
        create_new_player(cursor)
        player_name = 'Player1'
        high_score = 0
        character_level = 1
    else:
        # Player exists, load the first player's data
        player_name, high_score, character_level = player_data
        print(f"Loaded {player_name} with High Score: {high_score} and Level: {character_level}")

    # Initialize player object
    player = Player([5, 5], "up", high_score, character_level)
    watch_rate = 0.01
    welcometext = WelcomeText()


    def start_screen_update():
        nonlocal start_screen, game_playing, game_mode, refresh_rate, store_screen, round_num, radius_selected, cooldown_selected, game_state, coins, welcometext, start_time  # Declare as nonlocal
        stdscr.clear()
        # Overlay the "Game Over" message
        welcometext = WelcomeText()
        for i in range(8):
            stdscr.addstr(SIZE[0] // 2 - 15 + i, stdscr.getmaxyx()[1]//2 - len(welcometext.textlines[i])//2, welcometext.textlines[i])
        stdscr.addstr(SIZE[0] // 2 - 8, stdscr.getmaxyx()[1]//2 + 2*len(welcometext.textlines[0])//7 , "conway edition")
        stdscr.addstr(2 * SIZE[0] // 3 - 1, stdscr.getmaxyx()[1] // 6,f"Your high score is {high_score}")
        stdscr.addstr(2*SIZE[0] // 3 + 1, stdscr.getmaxyx()[1]//6, "Press 'e' to play easy mode or 'h' to for hard mode")
        stdscr.addstr(2*SIZE[0] // 3 + 3, stdscr.getmaxyx()[1]//6, "Press 's' to go to store / character setup")
        stdscr.addstr(2*SIZE[0] // 3 + 5, stdscr.getmaxyx()[1]//6, f"You have selected game mode: {game_mode}")
        stdscr.addstr(2*SIZE[0] // 3 + 7, stdscr.getmaxyx()[1]//6, f"Press ENTER to start !")

        coins = 0
        player.radius_level = 1
        player.cooldown_level = 1
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
            game_state = GameState.STORE_SCREEN
            radius_selected, cooldown_selected = reset_store()
        elif key == ord('j'):
            game_state = GameState.JUST_WATCHING
        elif key == curses.KEY_ENTER or key in [10, 13]:
            # Start the game
            game_state = GameState.GAME_PLAYING
            start_time = time.time()
            round_num = 1
        time.sleep(0.05)

    def store_screen_update():
        nonlocal start_screen, store_screen, radius_selected, cooldown_selected, coins, game_state
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
                coins -= 1

        elif key == curses.KEY_LEFT:

            if radius_selected:
                level_before = player.radius_level
                player.decrease_radius()
                level_after = player.radius_level
                if level_before != level_after:
                    coins += 1
            else:
                level_before = player.cooldown_level
                player.increase_cooldown()
                level_after = player.cooldown_level
                if level_before != level_after:
                    coins += 1
        elif key == ord("p"):
            coins += 10
        # Press 'r' to return to the start screen
        if key == ord("r"):
            game_state = GameState.START_SCREEN
        time.sleep(0.01)
        stdscr.refresh()

    def round_end_update():
        nonlocal start_screen, store_screen, radius_selected, cooldown_selected, coins, game_state, round_num, start_time
        stdscr.clear()
        # Overlay the "Game Over" message and store options
        stdscr.addstr(SIZE[0] // 2 - 10, SIZE[1] // 3, f"Congratulations, you beat round {round_num}!")
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

        stdscr.addstr(SIZE[0] // 2 + 10, SIZE[1] // 3, f"Press 'c' to proceed to round {round_num + 1}")

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
                coins -= 1

        elif key == curses.KEY_LEFT:

            if radius_selected:
                level_before = player.radius_level
                player.decrease_radius()
                level_after = player.radius_level
                if level_before != level_after:
                    coins += 1
            else:
                level_before = player.cooldown_level
                player.increase_cooldown()
                level_after = player.cooldown_level
                if level_before != level_after:
                    coins += 1

        elif key == ord("p"):
            coins += 10

        # Press 'r' to return to the start screen
        if key == ord("c"):
            round_num += 1
            game_state = GameState.GAME_PLAYING
            start_time = time.time()
        time.sleep(0.01)
        stdscr.refresh()

    def game_playing_update():
        nonlocal start_time, round_num, score, total_score, coins, matrix, snitch, last_hit_snitch, bullets, count, player_dead, game_playing, game_state, cursor, conn, high_score
        current_time = time.time()
        seconds = int(current_time - start_time)
        if int(current_time - start_time) > 20:
            time.sleep(0.5)
            game_state = GameState.ROUND_END
        # Print the game matrix with player position
        player_dead, hit_snitch = print_matrix(stdscr, matrix, player)
        if hit_snitch:
            if time.time() - 0.5 > last_hit_snitch:
                score += round_num
                if score >= high_score:
                    high_score = score
                total_score += 1
                coins += 1
                snitch.reset(stdscr)
                last_hit_snitch = time.time()

        if player_dead:

            cursor.execute('''
                            UPDATE player_data 
                            SET high_score = ?, character_level = ?
                            WHERE player_name = ?''', (high_score, character_level, player_name))
            conn.commit()
            player.high_score = high_score
            print_death_screen(stdscr, matrix, player)
            game_state = GameState.PLAYER_DEAD

        # Display the elapsed time and score
        stdscr.addstr(0, 0, f"  Coins: {coins}     Round: {round_num}     Score: {score}        Progress: |" + seconds * "-" + (
                    20 - seconds) * " " + '|')

        # Handle player movement
        player.move(stdscr, SIZE, bullets)

        # Update the bullets
        update_bullets(bullets, stdscr, SIZE)
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
                            if x in [max(0, bullet.position[0] - bullet.radius),
                                     min(len(matrix) - 1, bullet.position[0] + bullet.radius + 1) - 1] and y in [
                                max(0, bullet.position[1] - bullet.radius),
                                min(len(matrix[0]) - 1, bullet.position[1] + bullet.radius + 1) - 1]:
                                matrix[x, y] = 0
                            else:
                                matrix[x, y] = 4
                else:
                    # If no neighboring `1` is found, continue placing the bullet in the matrix
                    matrix[bullet.position[0], bullet.position[1]] = 3

            count = 0
        else:
            count += 1

        time.sleep(refresh_rate / round_num)

    def player_dead_update():
        nonlocal player_dead, score, start_screen, game_playing, store_screen, round_num, game_state, coins, start_time
        stdscr.clear()

        # Overlay the "Game Over" message
        stdscr.addstr(SIZE[0] // 2 - 1, SIZE[1] // 2 - 5, "GAME OVER!")
        stdscr.addstr(SIZE[0] // 2 + 1, SIZE[1] // 2 - 5,
                      "Press 'r' to reset, 's' to go back to the start screen, or 'q' to quit")
        stdscr.addstr(SIZE[0] // 2 + 3, SIZE[1] // 2 - 5, f"Your score was {score}!")
        stdscr.refresh()

        # Wait for the player's input
        key = stdscr.getch()
        if key == ord('q'):
            # Quit the game
            stdscr.addstr(SIZE[0] // 2 - 3, SIZE[1] // 2 - 5, "q pressed")
            return True # Exit the outer loop and end the game
        elif key == ord('s'):
            game_state = GameState.START_SCREEN
        elif key == ord('r'):
            # Reset the game
            game_state = GameState.GAME_PLAYING
            coins = 0
            player.radius_level = 1
            player.cooldown_level = 1
            round_num = 1
            start_time = time.time()

        time.sleep(0.05)

    def just_watching_update():
        nonlocal matrix, player, SIZE, game_state, watch_rate
        player.avatar = " "
        matrix = next_iteration(matrix, SIZE, player)
        print_matrix(stdscr, matrix, player)
        time.sleep(watch_rate)

        key = stdscr.getch()

        if key == ord('q'):
            game_state = GameState.START_SCREEN
        elif key == curses.KEY_LEFT:
            watch_rate *= 2
        elif key == curses.KEY_RIGHT:
            watch_rate /= 2

    def reset_game():
        nonlocal score
        SIZE = stdscr.getmaxyx()  # Fixed grid size for now, but you can adjust this if needed
        SIZE = (SIZE[0], SIZE[1] // 2)
        matrix = initlise_matrix(SIZE)

        snitch = Snitch([10,10])
        snitch.reset(stdscr)
        matrix[snitch.position[0], snitch.position[1]] = 2
        return SIZE, matrix, snitch

    def reset_store():
        return radius_selected, cooldown_selected


    # Outer loop that allows resetting the game
    while True:
        SIZE, matrix, snitch = reset_game()
        start_time = time.time()  # Record the start time when the game begins
        last_hit_snitch = time.time()
        try:
            while game_state == GameState.START_SCREEN:
                start_screen_update()
            while game_state == GameState.STORE_SCREEN:
                store_screen_update()
            while game_state == GameState.GAME_PLAYING:
                game_playing_update()
            while game_state == GameState.ROUND_END:
                round_end_update()
            while game_state == GameState.JUST_WATCHING:
                just_watching_update()
            while game_state == GameState.PLAYER_DEAD:
                if player_dead_update():
                    break

        except KeyboardInterrupt:
            return  # Handle Ctrl+C gracefully

    conn.close()
# Wrapper to run the curses-based main loop
curses.wrapper(main)
