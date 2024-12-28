# models.py

class Camel:
    """
    Represents a single camel in the Camel Up game.
    """

    def __init__(self, name, color=None):
        self.name = name
        self.position = 0  # The current tile index on the board
        self.color = color  # Add color attribute

    def __repr__(self):
        return f"Camel({self.name}, pos={self.position})"

    def colored_name(self):
        """
        Returns the camel's name wrapped in ANSI color codes if a color is set.
        """
        if self.color:
            return f"{self.color}{self.name}\033[0m"
        return self.name
