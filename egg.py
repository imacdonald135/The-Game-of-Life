import time
import random
import math

class Egg:

    def __init__(self, player, SIZE):

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

        self.coords = [block_center_x, block_center_y]
        self.time = time.time()