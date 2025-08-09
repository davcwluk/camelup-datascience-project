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
        
        # Dice tracking for turn-based system (reuse existing dice definitions)
        self.dice = {
            'Red': self.colored_faces,
            'Blue': self.colored_faces, 
            'Green': self.colored_faces,
            'Yellow': self.colored_faces,
            'Purple': self.colored_faces,
            'BW': self.bw_faces  # Use existing BW die system
        }
        self.used_dice = []  # Track which dice have been used in current leg
        
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
    
    def get_available_dice(self):
        """Get list of available dice colors for pyramid ticket action"""
        available = []
        for color in ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'BW']:
            if color not in self.used_dice:
                available.append(color)
        return available
    
    def roll_random_die(self):
        """Roll a random available die (for pyramid ticket action)"""
        available = self.get_available_dice()
        if not available:
            return None
        
        # Choose random color from available
        color = random.choice(available)
        # Mark this die as used
        self.used_dice.append(color)
        
        if color == 'BW':
            # BW die returns (steps, camel_color) - use existing roll_bw method
            result = self.roll_bw()
            steps, camel_color = result
            return camel_color, steps  # Return camel color and steps
        else:
            # Regular colored die
            steps = random.choice(self.dice[color])
            return color, steps
    
    def reset(self):
        """Reset dice for new leg"""
        self.used_dice = []
