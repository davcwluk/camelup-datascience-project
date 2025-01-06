# board.py

import sys
from .models import Camel  # Import Camel from models.py

class Board:
    """
    Manages the tiles and stacking of camels on those tiles.
    """

    def __init__(self, track_length):
        """
        Initializes the Board.

        Args:
            track_length (int, optional): Number of tiles in the track. Defaults to 16.
        """
        self.track_length = track_length
        # Each position is a list of camels (topmost last)
        self.tiles = [[] for _ in range(track_length + 1)]

    def initialize_camels(self, camels):
        """
        Initialize the board with camels at their starting positions.
        Forward-moving camels start at 0, backward-moving camels start at position 17 (off-board).
        """
        self.tiles = [[] for _ in range(self.track_length + 1)]  # Reset tiles
        
        for camel in camels:
            if camel.moves_backward:
                camel.position = 17  # Start outside the track
            else:
                camel.position = 0
                self.tiles[0].append(camel)

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
        Display the board in a horizontal line, showing all tiles and camels with stacking order.
        """
        tile_width = 20  # Increased to accommodate stacking symbols
        board_representation = []

        for pos in range(self.track_length + 1):
            camels_on_tile = self.tiles[pos]
            if len(camels_on_tile) > 1:
                # Show stacking with arrows (bottom → top)
                camel_stack = " → ".join(camel.colored_name() for camel in camels_on_tile)
                tile_str = f"[{pos:2d}: {camel_stack}]"
            elif len(camels_on_tile) == 1:
                # Single camel, no arrows needed
                tile_str = f"[{pos:2d}: {camels_on_tile[0].colored_name()}]"
            else:
                # Empty tile
                tile_str = f"[{pos:2d}:     ]"
            
            board_representation.append(tile_str)

        # Join all tile strings and print
        print(" ".join(board_representation))

    def __repr__(self):
        """
        Return a string representation of the board with tile numbers and camels.

        Tiles are displayed from start (0) to finish (16) horizontally.
        """
        return self.display_board()

    def move_camel(self, camel, steps):
        """
        Move a camel the specified number of steps.
        
        Args:
            camel (Camel): The camel to move
            steps (int): Number of steps to move
        """
        # Remove camel from current position
        current_pos = camel.position
        stack = self.tiles[current_pos]
        camel_index = stack.index(camel)
        moving_stack = stack[camel_index:]
        self.tiles[current_pos] = stack[:camel_index]
        
        # Calculate new position
        new_pos = min(current_pos + steps, self.track_length)
        
        # Update camel positions
        for c in moving_stack:
            c.position = new_pos
        
        # Add moving stack to new position
        self.tiles[new_pos].extend(moving_stack)

    def move_camel_initial_setup(self, camel, steps):
        """
        Move a single camel during initial setup, with stacking only if moving to an occupied position.
        Handles both forward and backward moving camels.
        """
        # Remove camel from current position if it's on the board
        if camel.position <= self.track_length:
            self.tiles[camel.position].remove(camel)
        
        # Calculate new position based on direction
        if camel.moves_backward:
            # Start counting from position 17, so moving 1 step puts it at 16
            new_pos = 17 - steps
            new_pos = max(0, new_pos)  # Don't go below 0
        else:
            new_pos = steps
        
        # Update camel position
        camel.position = new_pos
        
        # Add camel to new position (will stack on top if position is occupied)
        self.tiles[new_pos].append(camel)

    def move_camel_with_stack(self, camel, steps):
        """
        Move a camel and all camels stacked on top of it.
        """
        current_pos = camel.position
        stack = self.tiles[current_pos]
        camel_index = stack.index(camel)
        
        # Get all camels from this camel up
        moving_stack = stack[camel_index:]
        # Keep only camels below this one
        self.tiles[current_pos] = stack[:camel_index]
        
        # Calculate new position based on direction
        if camel.moves_backward:
            new_pos = current_pos - steps
            new_pos = max(0, new_pos)
        else:
            new_pos = min(current_pos + steps, self.track_length)
        
        # Update positions for all moving camels
        for c in moving_stack:
            c.position = new_pos
        
        # Add moving stack to top of any existing camels at new position
        self.tiles[new_pos].extend(moving_stack)
