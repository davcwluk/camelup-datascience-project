# dice.py
import random

class Dice:
    """
    Manages dice rolls for the Camel Up game.
    """
    def __init__(self):
        # Regular dice for colored camels (each value appears twice)
        self.colored_faces = [1, 1, 2, 2, 3, 3]
        # Separate dice for black and white initial setup
        self.special_faces = [1, 2, 3]
        # Combined dice for black/white during main game
        self.bw_faces = [(1, 'White'), (2, 'White'), (3, 'White'),
                        (1, 'Black'), (2, 'Black'), (3, 'Black')]
        
    def roll(self):
        """Generic roll for initial setup - uses colored dice faces"""
        return random.choice(self.colored_faces)
        
    def roll_colored(self):
        """Roll a regular colored dice"""
        return random.choice(self.colored_faces)
        
    def roll_special_initial(self):
        """Roll for initial black/white setup - returns steps only"""
        return random.choice(self.special_faces)
        
    def roll_bw(self):
        """Roll for black/white movement during main game"""
        return random.choice(self.bw_faces)
