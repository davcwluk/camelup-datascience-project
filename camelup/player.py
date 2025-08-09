# player.py

class Player:
    """
    Represents a player in the Camel Up game with betting capabilities.
    """
    
    def __init__(self, name, starting_money=3):
        self.name = name
        self.money = starting_money
        self.bets = []  # List of active bets
        self.bet_history = []  # Complete betting history for analysis
        self.finish_cards_remaining = 5  # 5 finish cards for race winner/loser betting
        self.pyramid_tickets = 0  # Pyramid tickets collected during leg
        
    def place_bet(self, bet):
        """Place a bet - no upfront cost in Camel Up"""
        # In Camel Up, placing bets costs nothing upfront
        # Players either get immediate rewards (leg betting) or pay/receive at resolution
        self.bets.append(bet)
        self.bet_history.append(bet)
        return True
    
    def receive_payout(self, amount):
        """Receive money from winning bet or bank"""
        self.money = max(0, self.money + amount)  # Cannot go below 0 EP
    
    def use_finish_card(self):
        """Use one finish card for race betting"""
        if self.finish_cards_remaining > 0:
            self.finish_cards_remaining -= 1
            return True
        return False
    
    def can_place_race_bet(self):
        """Check if player has finish cards for race betting"""
        return self.finish_cards_remaining > 0
    
    def add_pyramid_ticket(self):
        """Add a pyramid ticket"""
        self.pyramid_tickets += 1
    
    def collect_pyramid_payouts(self):
        """Collect 1 EP per pyramid ticket at end of leg"""
        payout = self.pyramid_tickets
        self.money += payout
        self.pyramid_tickets = 0  # Reset for next leg
        return payout
    
    def clear_leg_bets(self):
        """Clear leg-specific bets at end of round"""
        self.bets = [bet for bet in self.bets if bet.bet_type == 'race_winner']
    
    def get_active_bets(self, bet_type=None):
        """Get active bets, optionally filtered by type"""
        if bet_type:
            return [bet for bet in self.bets if bet.bet_type == bet_type]
        return self.bets
    
    def __repr__(self):
        return f"Player({self.name}, {self.money} EP)"


class HumanPlayer(Player):
    """Human player with interactive betting interface"""
    pass


class BotPlayer(Player):
    """Bot player with automated betting strategy"""
    
    def __init__(self, name, starting_money=3, strategy=None):
        super().__init__(name, starting_money)
        self.strategy = strategy or 'random'
    
    def decide_bet(self, available_bets, game_state):
        """AI decides what bet to place based on strategy"""
        if self.strategy == 'random':
            return self._random_strategy(available_bets)
        elif self.strategy == 'probability':
            return self._probability_strategy(available_bets, game_state)
        elif self.strategy == 'conservative':
            return self._conservative_strategy(available_bets)
        elif self.strategy == 'aggressive':
            return self._aggressive_strategy(available_bets)
        return None
    
    def _random_strategy(self, available_bets):
        """Place random bets"""
        import random
        if available_bets and random.random() > 0.3:  # 70% chance to bet
            return random.choice(available_bets)
        return None
    
    def _probability_strategy(self, available_bets, game_state):
        """Bet based on calculated probabilities"""
        # Will integrate with ProbabilityCalculator
        return self._random_strategy(available_bets)  # Placeholder
    
    def _conservative_strategy(self, available_bets):
        """Only bet on high-probability, low-risk outcomes"""
        return None  # Very conservative, rarely bets
    
    def _aggressive_strategy(self, available_bets):
        """Bet frequently on higher-payout outcomes"""
        import random
        if available_bets:
            return random.choice(available_bets)
        return None