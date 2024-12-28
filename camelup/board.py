# board.py

import sys
from .models import Camel  # Import Camel from models.py

class Board:
    """
    Manages the tiles and stacking of camels on those tiles.
    """

    def __init__(self, track_length=16):
        """
        Initializes the Board.

        Args:
            track_length (int, optional): Number of tiles in the track. Defaults to 16.
        """
        self.track_length = track_length
        # Each position is a list of camels (topmost last)
        self.tiles = [[] for _ in range(self.track_length + 1)]

    def place_camel(self, camel, position=0):
        """
        Place a single camel on the specified tile.

        Args:
            camel (Camel): The camel to place.
            position (int, optional): Tile index. Defaults to 0.
        """
        camel.position = position
        self.tiles[position].append(camel)

    def move_camel_stack(self, camel, steps):
        """
        Move the given camel and any camels above it in the stack by 'steps'.

        Args:
            camel (Camel): The camel to move.
            steps (int): Number of tiles to move forward.
        """
        old_pos = camel.position
        stack = self.tiles[old_pos]

        if camel not in stack:
            raise ValueError(f"{camel.name} is not on tile {old_pos} as expected.")

        # Identify the camel's position in the stack
        index_in_stack = stack.index(camel)
        # This slice includes 'camel' and any camels above it
        moving_stack = stack[index_in_stack:]
        # Remove them from the old tile
        self.tiles[old_pos] = stack[:index_in_stack]

        # Calculate new position (clamped to track_length)
        new_pos = min(old_pos + steps, self.track_length)
        # Update positions for all camels that moved
        for c in moving_stack:
            c.position = new_pos

        # Place the moving stack on top of the new tile
        self.tiles[new_pos].extend(moving_stack)

    def get_tile_stack(self, position):
        """
        Return the list of camels at the specified tile.

        Args:
            position (int): Tile index.

        Returns:
            list: List of camels on the tile.
        """
        return self.tiles[position]

    def is_finished(self):
        """
        Check if any camel has reached or passed the last tile.

        Returns:
            bool: True if the race is over, False otherwise.
        """
        for tile_index in range(self.track_length, -1, -1):
            if self.tiles[tile_index]:
                return True
        return False

    def get_winning_camel(self):
        """
        Return the camel on top of the furthest occupied tile.

        Returns:
            Camel or None: The winning camel or None if no winner yet.
        """
        for tile_index in range(self.track_length, -1, -1):
            if self.tiles[tile_index]:
                return self.tiles[tile_index][-1]  # Topmost camel
        return None

    def display_board(self):
        """
        Display the board in a horizontal line, showing all tiles and camels.
        """
        # Increased tile_width to accommodate colored text
        tile_width = 20  
        board_representation = []

        for pos in range(self.track_length + 1):
            # Get camels on this tile and join their colored names
            camels_on_tile = ', '.join(camel.colored_name() for camel in self.tiles[pos])
            # Add padding after the position number
            tile_str = f"[{pos:2d}: {camels_on_tile}]"
            board_representation.append(tile_str)

        # Join all tile strings and print
        print(" ".join(board_representation))

    def __repr__(self):
        """
        Return a string representation of the board with tile numbers and camels.

        Tiles are displayed from start (0) to finish (16) horizontally.
        """
        return self.display_board()
