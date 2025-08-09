# betting.py

import random

class Bet:
    """Base class for all bet types"""
    
    def __init__(self, player_name, bet_type, amount, target=None):
        self.player_name = player_name
        self.bet_type = bet_type  # 'race_winner', 'leg_winner', 'race_loser'
        self.amount = amount
        self.target = target  # Camel being bet on
        self.odds = 1  # Payout multiplier
        self.resolved = False
        self.won = False
        
    def calculate_payout(self):
        """Calculate payout if bet wins"""
        if self.won:
            return self.amount * self.odds
        return 0
    
    def __repr__(self):
        status = "WON" if self.won else "LOST" if self.resolved else "ACTIVE"
        return f"Bet({self.player_name}: {self.amount} EP on {self.target} to {self.bet_type}, {status})"


class RaceWinnerBet(Bet):
    """Bet on overall race winner - place finish card in deck"""
    
    def __init__(self, player_name, camel):
        super().__init__(player_name, 'race_winner', 0, camel)  # No upfront cost
        self.deck_position = None  # Will be set when card is drawn from deck
        
    def calculate_race_payout(self, won, deck_position):
        """Calculate race payout based on position when card is drawn from deck"""
        if won:
            payouts = [8, 5, 3, 2, 1]  # 1st through 5th card drawn showing winner
            if deck_position <= len(payouts):
                return payouts[deck_position - 1]
            else:
                return -1  # 6th+ card penalty
        else:
            return -1  # Wrong bet penalty


class LegWinnerBet(Bet):
    """Bet on leg (round) winner - take betting ticket"""
    
    def __init__(self, player_name, camel, ticket_value):
        super().__init__(player_name, 'leg_winner', 0, camel)  # No upfront cost
        self.ticket_value = ticket_value  # 5, 3, 2 for potential winnings
        
    def calculate_leg_payout(self, camel_position):
        """Calculate final leg payout based on camel's finishing position"""
        if camel_position == 1:  # Leading camel (1st place)
            return self.ticket_value  # Win the full ticket value (5, 3, or 2 EP)
        elif camel_position == 2:  # Second place  
            return 1  # Win 1 EP
        else:  # Any other racing camel (3rd, 4th, 5th place)
            return -1  # Lose 1 EP


class RaceLoserBet(Bet):
    """Bet on which camel will finish last in the race"""
    
    def __init__(self, player_name, camel):
        super().__init__(player_name, 'race_loser', 0, camel)  # No upfront cost
        self.deck_position = None  # Will be set when card is drawn from deck
        
    def calculate_race_payout(self, won, deck_position):
        """Calculate race payout based on position when card is drawn from deck"""
        if won:
            payouts = [8, 5, 3, 2, 1]  # 1st through 5th card drawn showing loser
            if deck_position <= len(payouts):
                return payouts[deck_position - 1]
            else:
                return -1  # 6th+ card penalty
        else:
            return -1  # Wrong bet penalty


class BettingManager:
    """Manages all betting operations"""
    
    def __init__(self):
        self.active_bets = []
        self.resolved_bets = []
        self.leg_winner_tickets = {}  # Track available betting tickets
        self.race_winner_decks = {}  # Card decks for race winner bets
        self.race_loser_decks = {}   # Card decks for race loser bets
        self._initialize_leg_tickets()
        self._initialize_race_decks()
    
    def _initialize_leg_tickets(self):
        """Initialize leg winner betting tickets for each camel"""
        colors = ['Red', 'Blue', 'Green', 'Yellow', 'Purple']
        for color in colors:
            self.leg_winner_tickets[color] = [5, 3, 2]  # Available ticket values
    
    def _initialize_race_decks(self):
        """Initialize race betting card decks for each camel"""
        colors = ['Red', 'Blue', 'Green', 'Yellow', 'Purple']
        for color in colors:
            self.race_winner_decks[color] = []  # Cards placed face down
            self.race_loser_decks[color] = []   # Cards placed face down
    
    def get_available_race_bets(self, camels):
        """Get available race winner bets"""
        available = []
        colors = [c.name for c in camels if not c.moves_backward]
        for camel_name in colors:
            available.append(('race_winner', camel_name))  # type, camel
        return available
    
    def get_available_leg_bets(self, camels):
        """Get available leg winner bets"""
        available = []
        for camel in camels:
            if not camel.moves_backward and camel.name in self.leg_winner_tickets:
                tickets_left = self.leg_winner_tickets[camel.name]
                if tickets_left:
                    ticket_value = tickets_left[0]  # Top ticket value
                    available.append(('leg_winner', camel.name, ticket_value))  # type, camel, ticket_value
        return available
    
    def get_available_race_loser_bets(self, camels):
        """Get available race loser bets"""
        available = []
        colors = [c.name for c in camels if not c.moves_backward]
        for camel_name in colors:
            available.append(('race_loser', camel_name))  # type, camel
        return available
    
    def place_bet(self, player, bet_info):
        """Place a bet for a player"""
        bet_type = bet_info[0]
        camel_name = bet_info[1]
        
        if bet_type == 'race_winner':
            # Check if player has finish cards remaining
            if not player.can_place_race_bet():
                return False
            bet = RaceWinnerBet(player.name, camel_name)
            # Use one finish card
            player.use_finish_card()
            # Add card to the deck face down
            self.race_winner_decks[camel_name].append(bet)
        elif bet_type == 'leg_winner':
            ticket_value = bet_info[2]
            bet = LegWinnerBet(player.name, camel_name, ticket_value)
            # Remove the ticket from available (no immediate reward)
            if camel_name in self.leg_winner_tickets and self.leg_winner_tickets[camel_name]:
                self.leg_winner_tickets[camel_name].pop(0)
        elif bet_type == 'race_loser':
            # Check if player has finish cards remaining
            if not player.can_place_race_bet():
                return False
            bet = RaceLoserBet(player.name, camel_name)
            # Use one finish card
            player.use_finish_card()
            # Add card to the deck face down
            self.race_loser_decks[camel_name].append(bet)
        else:
            return False
        
        # No upfront cost - player just takes the betting position
        player.bets.append(bet)
        player.bet_history.append(bet)
        self.active_bets.append(bet)
        return True
    
    def resolve_leg_bets(self, leg_results):
        """Resolve leg winner bets based on round results"""
        # leg_results should be list of camels in finishing order (furthest to closest)
        resolved = []
        
        for bet in self.active_bets:
            if bet.bet_type == 'leg_winner' and not bet.resolved:
                # Find the position of the bet's target camel
                camel_position = None
                for i, camel in enumerate(leg_results):
                    if camel.name == bet.target:
                        camel_position = i + 1  # 1st, 2nd, 3rd, etc.
                        break
                
                if camel_position:
                    # Calculate payout based on final position
                    payout = bet.calculate_leg_payout(camel_position)
                    bet.leg_payout = payout
                
                bet.resolved = True
                resolved.append(bet)
        
        # Move resolved bets
        for bet in resolved:
            self.active_bets.remove(bet)
            self.resolved_bets.append(bet)
        
        return resolved
    
    def resolve_race_bets(self, final_results):
        """Resolve race winner and race loser bets using deck-based system"""
        resolved = []
        winner = final_results[0] if final_results else None
        loser = final_results[-1] if final_results else None
        
        # Resolve race winner bets using deck system
        if winner:
            winner_deck = self.race_winner_decks[winner.name].copy()
            random.shuffle(winner_deck)  # Shuffle deck before drawing
            
            for i, bet in enumerate(winner_deck):
                deck_position = i + 1  # 1st, 2nd, 3rd, etc. card drawn
                bet.won = True
                bet.deck_position = deck_position
                bet.payout = bet.calculate_race_payout(True, deck_position)
                bet.resolved = True
                resolved.append(bet)
        
        # Resolve losing race winner bets
        for camel_name, deck in self.race_winner_decks.items():
            if camel_name != (winner.name if winner else None):
                for bet in deck:
                    bet.won = False
                    bet.payout = bet.calculate_race_payout(False, 0)
                    bet.resolved = True
                    resolved.append(bet)
        
        # Resolve race loser bets using deck system  
        if loser:
            loser_deck = self.race_loser_decks[loser.name].copy()
            random.shuffle(loser_deck)  # Shuffle deck before drawing
            
            for i, bet in enumerate(loser_deck):
                deck_position = i + 1  # 1st, 2nd, 3rd, etc. card drawn
                bet.won = True
                bet.deck_position = deck_position
                bet.payout = bet.calculate_race_payout(True, deck_position)
                bet.resolved = True
                resolved.append(bet)
        
        # Resolve losing race loser bets
        for camel_name, deck in self.race_loser_decks.items():
            if camel_name != (loser.name if loser else None):
                for bet in deck:
                    bet.won = False
                    bet.payout = bet.calculate_race_payout(False, 0)
                    bet.resolved = True
                    resolved.append(bet)
        
        # Move resolved bets
        for bet in resolved:
            if bet in self.active_bets:
                self.active_bets.remove(bet)
            self.resolved_bets.append(bet)
        
        return resolved
    
    def reset_leg_tickets(self):
        """Reset leg winner tickets for new round"""
        self._initialize_leg_tickets()
    
    def get_betting_summary(self):
        """Get summary of all betting activity"""
        summary = {
            'active_bets': len(self.active_bets),
            'resolved_bets': len(self.resolved_bets),
            'total_wagered': sum(bet.amount for bet in self.resolved_bets + self.active_bets),
            'total_payouts': sum(bet.calculate_payout() for bet in self.resolved_bets)
        }
        return summary