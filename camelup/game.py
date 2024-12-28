# game.py

import random

from .models import Camel
from .board import Board
from .dice import Dice

class CamelUpGame:
    """
    Manages the overall state and rules of the Camel Up game.
    """

    def __init__(self, num_camels=7, track_length=16):
        # Create the board
        self.board = Board(track_length=track_length)

        # Define colors with ANSI codes
        COLORS = {
            "Red": "\033[31m",
            "Blue": "\033[34m",
            "Green": "\033[32m",
            "Yellow": "\033[33m",
            "Purple": "\033[35m",
            "White": "\033[37m",
            "Black": "\033[30m"
        }

        # Create camels with colors
        self.camels = [
            Camel(name, color) 
            for name, color in list(COLORS.items())[:num_camels]
        ]

        # Place all camels at the start tile (0)
        for camel in self.camels:
            self.board.place_camel(camel, position=0)

        # Dice instance (one die set for all camels, or multiple if you prefer)
        self.dice = Dice(die_faces=[1,2,3])

        # Track which camels have moved in this "leg"
        self.camels_moved_this_leg = set()

    def roll_die_and_move(self):
        """
        Roll the die for one of the camels that hasn't moved yet.
        """
        available_camels = [
            c for c in self.camels
            if c not in self.camels_moved_this_leg
        ]
        if not available_camels:
            # All camels have moved this leg
            return None

        # Choose a random camel that hasn't moved
        chosen_camel = random.choice(available_camels)
        steps = self.dice.roll()

        # Move on the board
        self.board.move_camel_stack(chosen_camel, steps)
        self.camels_moved_this_leg.add(chosen_camel)

        return chosen_camel, steps

    def reset_leg(self):
        """
        Reset any leg-specific state (e.g., which camels have moved).
        """
        self.camels_moved_this_leg.clear()

    def is_race_finished(self):
        """
        Check if the race is over.
        """
        return self.board.is_finished()

    def get_winner(self):
        """
        Return the winning camel (if race is finished).
        """
        return self.board.get_winning_camel()

    def print_board_state(self):
        """
        Print the board layout for debugging/visualization.
        """
        print(self.board)
        print("-" * 40)
