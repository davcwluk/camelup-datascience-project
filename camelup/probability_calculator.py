from copy import deepcopy
from typing import List, Dict
from collections import defaultdict
from .models import Camel
from .board import Board

class ProbabilityCalculator:
    def __init__(self, game):
        self.game = game
        
    def calculate_possible_outcomes(self, available_dice: List[str]) -> tuple[List[str], Dict[str, float]]:
        """
        Calculate all possible outcomes and probabilities for the remaining dice.
        """
        outcomes = []
        leading_counts = defaultdict(int)
        
        # Calculate total faces based on available dice
        total_scenarios = len(available_dice) * 6  # Each dice has 6 faces
        
        for dice_color in available_dice:
            if dice_color == 'BW':
                # Each BW outcome has equal 1/6 probability
                for steps, color in self.game.dice.bw_faces:
                    dice_camel = next(c for c in self.game.camels if c.name == color)
                    leading_camel = self._simulate_move(dice_color, steps, special_color=color)
                    if leading_camel and not leading_camel.moves_backward:
                        leading_counts[leading_camel.name] += 1
                        leading_camel_obj = next(c for c in self.game.camels if c.name == leading_camel.name)
                        outcome = (f"If {dice_camel.colored_name()} dice is drawn with value of {steps}, "
                                 f"{leading_camel_obj.colored_name()} will be leading")
                        outcomes.append(outcome)
            else:
                # Each colored dice has 6 faces (1,1,2,2,3,3)
                dice_camel = next(c for c in self.game.camels if c.name == dice_color)
                for steps in [1, 2, 3]:  # Only iterate unique values
                    leading_camel = self._simulate_move(dice_color, steps)
                    if leading_camel and not leading_camel.moves_backward:
                        leading_counts[leading_camel.name] += 2  # Count twice for each value
                        leading_camel_obj = next(c for c in self.game.camels if c.name == leading_camel.name)
                        outcome = (f"If {dice_camel.colored_name()} dice is drawn with value of {steps}, "
                                 f"{leading_camel_obj.colored_name()} will be leading")
                        outcomes.append(outcome)
        
        # Add empty line and probability messages
        outcomes.append("")
        for camel_name, count in leading_counts.items():
            camel_obj = next(c for c in self.game.camels if c.name == camel_name)
            prob_percentage = (count / total_scenarios) * 100
            prob_msg = (f"{camel_obj.colored_name()} has {count}/{total_scenarios} = "
                       f"{prob_percentage:.1f}% probability to be leading")
            outcomes.append(prob_msg)
        
        return outcomes, leading_counts

    def _simulate_move(self, dice_color: str, steps: int, special_color: str = None) -> Camel:
        """
        Simulate a single dice roll and movement to determine the leading camel.
        """
        board_copy = deepcopy(self.game.board)
        if dice_color == 'BW':
            camel = next(c for c in self.game.camels if c.name == special_color)
        else:
            camel = next(c for c in self.game.camels if c.name == dice_color)
        board_copy.move_camel_with_stack(camel, steps)
        return self._get_leading_normal_camel(board_copy)
            
    def _get_leading_normal_camel(self, board: Board) -> Camel:
        """Find the leading non-crazy camel on the board"""
        for pos in range(board.track_length, -1, -1):
            for camel in reversed(board.tiles[pos]):
                if not camel.moves_backward:
                    return camel
        return None 