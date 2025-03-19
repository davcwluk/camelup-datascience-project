from copy import deepcopy
import random
from typing import Dict, List, Tuple
from collections import defaultdict

class ExpectedValueCalculator:
    """
    Calculates the expected values (EVs) of different player actions in Camel Up
    without modifying the core game mechanics.
    """
    
    def __init__(self, game):
        """
        Initialize with a reference to the game state.
        
        Args:
            game: A CamelUpGame instance representing the current state
        """
        self.game = game
        # Track remaining betting tickets for each camel
        self.remaining_tickets = {camel.name: 4 for camel in self.game.camels if not camel.moves_backward}
        # Track which ticket number has been taken for each camel (for payout calculation)
        self.ticket_positions = {camel.name: 0 for camel in self.game.camels if not camel.moves_backward}
        
    def calculate_action_evs(self, num_simulations=1000) -> Dict[str, float]:
        """
        Calculate expected values for all possible player actions.
        
        Args:
            num_simulations: Number of simulations to run for each action
            
        Returns:
            Dictionary mapping action names to their expected values
        """
        actions = {}
        
        # 1. Take pyramid ticket (roll dice) - always 1 coin
        actions["Take Pyramid Ticket"] = 1.0
        
        # 2. Betting tickets - bet on which camel will be in first place at the end of the leg
        betting_evs = self.calculate_leg_bet_evs(num_simulations)
        
        # Add each available camel bet as a separate action
        for camel_name, ev in betting_evs.items():
            # Only include camels that still have betting tickets available
            if self.remaining_tickets.get(camel_name, 0) > 0:
                camel_obj = next(c for c in self.game.camels if c.name == camel_name)
                ticket_position = self.ticket_positions[camel_name] + 1  # Next position to be taken
                actions[f"Betting Ticket on {camel_obj.colored_name()} (ticket #{ticket_position})"] = ev
        
        # 3-4. Additional actions would be calculated here
        # (To be implemented in future versions)
        
        return actions
    
    def display_action_evs(self) -> List[str]:
        """
        Generate a formatted list of available actions and their EVs.
        
        Returns:
            List of formatted strings showing actions and their EVs
        """
        actions = self.calculate_action_evs()
        result = ["", "Available Actions and Expected Values:"]
        
        for action, ev in actions.items():
            result.append(f"• {action}: Expected Value = {ev:.2f} coins")
            
        # Add details for leg bets on each camel
        leg_bet_evs = self.calculate_leg_bet_evs(num_simulations=1000)
        result.append("")
        result.append("Detailed Leg Betting Ticket EVs:")
        
        for camel_name, ev in sorted(leg_bet_evs.items(), key=lambda x: x[1], reverse=True):
            camel_obj = next(c for c in self.game.camels if c.name == camel_name)
            tickets_left = self.remaining_tickets.get(camel_name, 0)
            next_position = self.ticket_positions[camel_name] + 1
            
            # Show availability of tickets and next position
            availability = f"({tickets_left} tickets left, next is ticket #{next_position})" if tickets_left > 0 else "(no tickets left)"
            result.append(f"  - {camel_obj.colored_name()}: {ev:.2f} {availability}")
            
        return result
    
    def calculate_leg_bet_evs(self, num_simulations=1000) -> Dict[str, float]:
        """
        Calculate the expected value of betting on each camel to win the current leg.
        
        Args:
            num_simulations: Number of simulations to run
            
        Returns:
            Dictionary mapping camel names to their expected values
        """
        # Payouts for leg bets based on ticket position (not camel position)
        # The payouts are only given if the camel comes in first
        # 1st ticket: 5 gold
        # 2nd ticket: 3 gold
        # 3rd ticket: 2 gold
        # 4th ticket: 1 gold
        position_payouts = {
            1: 5,  # 1st ticket: 5 gold
            2: 3,  # 2nd ticket: 3 gold
            3: 2,  # 3rd ticket: 2 gold
            4: 1,  # 4th ticket: 1 gold
        }
        
        # Initialize results for all forward-moving camels
        results = {}
        for camel in self.game.camels:
            if not camel.moves_backward:
                results[camel.name] = 0
        
        # Run simulations
        for _ in range(num_simulations):
            # Create a deep copy to avoid modifying the original game
            game_copy = deepcopy(self.game)
            
            # Simulate remaining dice rolls for this leg
            available_dice = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'BW']
            available_dice = [d for d in available_dice if d not in game_copy.moved_this_leg]
            dice_rolled = 0
            
            while dice_rolled < len(available_dice):
                if not available_dice:
                    break
                    
                # Randomly select and remove a dice
                selected_dice = random.choice(available_dice)
                available_dice.remove(selected_dice)
                
                if selected_dice == 'BW':
                    steps, color = game_copy.dice.roll_bw()
                    move_camel = next(c for c in game_copy.camels if c.name == color)
                else:
                    steps = game_copy.dice.roll_colored()
                    move_camel = next(c for c in game_copy.camels if c.name == selected_dice)
                    
                # Move the camel
                game_copy.board.move_camel_with_stack(move_camel, steps)
                game_copy.moved_this_leg.add(selected_dice)
                dice_rolled += 1
            
            # Get the final ranking for this leg
            ranking = []
            for pos in range(game_copy.board.track_length, -1, -1):
                for c in reversed(game_copy.board.tiles[pos]):
                    if not c.moves_backward:
                        ranking.append(c)
            
            # Only the camel in first place pays out
            if ranking:
                winning_camel = ranking[0]
                # Get the next ticket position for this camel
                next_position = self.ticket_positions[winning_camel.name] + 1
                # Add the payout for this position
                if next_position in position_payouts:
                    results[winning_camel.name] += position_payouts[next_position] / num_simulations
        
        return results
    
    def take_betting_ticket(self, camel_name: str) -> bool:
        """
        Take a betting ticket for the specified camel.
        
        Args:
            camel_name: The name of the camel to bet on
        
        Returns:
            True if the ticket was successfully taken, False otherwise
        """
        # Check if tickets are available for this camel
        if self.remaining_tickets.get(camel_name, 0) > 0:
            self.remaining_tickets[camel_name] -= 1
            self.ticket_positions[camel_name] += 1
            return True
        return False
    
    def simulate_action_outcomes(self, action_type: str, params: Dict = None, 
                               num_simulations: int = 1000) -> Tuple[float, Dict]:
        """
        Simulate outcomes of a specific action to calculate its expected value.
        This does not modify the actual game state.
        
        Args:
            action_type: Type of action ('pyramid_ticket', 'leg_bet', etc.)
            params: Parameters for the action (e.g., camel to bet on)
            num_simulations: Number of simulations to run
            
        Returns:
            Tuple of (expected value, outcome distribution)
        """
        if action_type == "Take Pyramid Ticket":
            return 1.0, {"success": 1.0}
        
        elif action_type == "Betting Ticket":
            if params and 'camel' in params:
                camel_name = params['camel']
                # Check if tickets are available
                if self.remaining_tickets.get(camel_name, 0) > 0:
                    leg_bet_evs = self.calculate_leg_bet_evs(num_simulations)
                    return leg_bet_evs.get(camel_name, 0), {
                        "tickets_left": self.remaining_tickets[camel_name] - 1,
                        "ticket_position": self.ticket_positions[camel_name] + 1
                    }
                else:
                    return 0.0, {"error": "No tickets available"}
            else:
                # Find best available camel bet
                leg_bet_evs = self.calculate_leg_bet_evs(num_simulations)
                
                # Filter to only include camels with available tickets
                available_bets = {camel: ev for camel, ev in leg_bet_evs.items() 
                                if self.remaining_tickets.get(camel, 0) > 0}
                
                if available_bets:
                    best_camel, best_ev = max(available_bets.items(), key=lambda x: x[1])
                    return best_ev, {
                        "camel": best_camel, 
                        "tickets_left": self.remaining_tickets[best_camel] - 1,
                        "ticket_position": self.ticket_positions[best_camel] + 1
                    }
                else:
                    return 0.0, {"error": "No tickets available for any camel"}
        
        # Placeholder for future action types
        return 0.0, {"unknown": 1.0} 