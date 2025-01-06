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
        self.board = Board(track_length)

        # Dice instance (one die set for all camels, or multiple if you prefer)
        self.dice = Dice()

        # Track which camels have moved in this "leg"
        self.moved_this_leg = set()

        # Number of camels
        self.num_camels = num_camels

        # Camels (will be initialized in main.py)
        self.camels = []

    def initialize_board(self, camels):
        """Initialize the board with the provided camels"""
        self.camels = camels
        self.board.initialize_camels(self.camels)

    def roll_die_and_move(self):
        """
        Roll the die for one of the camels that hasn't moved yet.
        """
        available_camels = [c for c in self.camels if c not in self.moved_this_leg]
        if not available_camels:
            # All camels have moved this leg
            return None

        # Choose a random camel that hasn't moved
        camel = available_camels[0]  # We'll modify this later for random selection
        steps = self.dice.roll()

        # Move on the board
        self.board.move_camel(camel, steps)
        self.moved_this_leg.add(camel)

        return camel, steps

    def reset_leg(self):
        """
        Reset any leg-specific state (e.g., which camels have moved).
        """
        self.moved_this_leg.clear()

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
