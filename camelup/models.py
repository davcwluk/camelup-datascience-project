# models.py

class Camel:
    """
    Represents a single camel in the Camel Up game.
    """

    def __init__(self, name, color=None, moves_backward=False):
        self.name = name
        self.position = 0 if not moves_backward else 16
        self.color = color
        self.moves_backward = moves_backward

    def __repr__(self):
        direction = "backward" if self.moves_backward else "forward"
        return f"Camel({self.name}, pos={self.position}, {direction})"

    def __eq__(self, other):
        if not isinstance(other, Camel):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def colored_name(self):
        """
        Returns the camel's name wrapped in ANSI color codes if a color is set.
        """
        if self.color:
            return f"{self.color}{self.name}\033[0m"
        return self.name
