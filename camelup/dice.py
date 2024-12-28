# dice.py
import random

class Dice:
    """
    Manages dice rolls for the Camel Up game.
    """

    def __init__(self, die_faces=None):
        # By default, standard Camel Up dice faces are [1, 2, 3]
        self.die_faces = die_faces if die_faces is not None else [1, 2, 3]

    def roll(self):
        """
        Return a random face from the die.
        """
        return random.choice(self.die_faces)
