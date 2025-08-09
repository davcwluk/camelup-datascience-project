# game_manager.py

from .game import CamelUpGame
from .player import Player, HumanPlayer, BotPlayer
from .betting import BettingManager
from .probability_calculator import ProbabilityCalculator
from .spectator_tiles import SpectatorTileManager, PyramidTicketManager
from .turn_manager import TurnManager

class GameManager:
    """
    Manages the complete Camel Up game including players, betting, and game flow
    """
    
    def __init__(self, players=None, num_camels=7, track_length=16):
        self.game = CamelUpGame(num_camels, track_length)
        self.betting_manager = BettingManager()
        self.spectator_tile_manager = SpectatorTileManager(track_length)
        self.pyramid_ticket_manager = PyramidTicketManager()
        self.players = []
        self.current_round = 0
        self.game_finished = False
        self.winner = None
        self.bank = 1000  # Bank for spectator tile and pyramid ticket payouts
        self.turn_manager = None  # Will be initialized after players are added
        
        # Game statistics for data science analysis
        self.game_stats = {
            'rounds_played': 0,
            'total_bets_placed': 0,
            'total_money_wagered': 0,
            'player_performances': {},
            'betting_decisions': []
        }
        
        # Add players if provided
        if players:
            for player in players:
                self.add_player(player)
    
    def add_player(self, player):
        """Add a player to the game"""
        self.players.append(player)
        self.game_stats['player_performances'][player.name] = {
            'starting_money': player.money,
            'final_money': 0,
            'bets_placed': 0,
            'bets_won': 0,
            'roi': 0.0
        }
    
    def initialize_game(self, camels):
        """Initialize the game with camels and allow initial race bets"""
        self.game.initialize_board(camels)
        
        # Connect spectator tile manager to board
        self.game.board.spectator_tile_manager = self.spectator_tile_manager
        
        # Initialize turn manager
        self.turn_manager = TurnManager(
            self.players, 
            self.game, 
            self.betting_manager,
            self.spectator_tile_manager,
            self.pyramid_ticket_manager,
            self  # Pass game manager for bank access
        )
        
        print(f"\nGame starting with {len(self.players)} players!")
        print("Players can place race bets at any time during the game using Action 4.")
        
    def _betting_phase_race_bets(self):
        """Handle initial race winner and race loser betting"""
        race_winner_bets = self.betting_manager.get_available_race_bets(self.game.camels)
        race_loser_bets = self.betting_manager.get_available_race_loser_bets(self.game.camels)
        
        for player in self.players:
            if not player.can_place_race_bet():
                print(f"\n{player.name} has no finish cards remaining - cannot place race bets")
                continue
                
            print(f"\n{player.name}'s turn ({player.money} EP, {player.finish_cards_remaining} finish cards)")
            
            if isinstance(player, HumanPlayer):
                self._human_race_betting(player, race_winner_bets, race_loser_bets)
            else:
                self._bot_race_betting(player, race_winner_bets, race_loser_bets)
    
    def _human_race_betting(self, player, winner_bets, loser_bets):
        """Handle human player race betting"""
        print("Available race winner bets:")
        for i, (_, camel) in enumerate(winner_bets):
            print(f"{i+1}. Bet on {camel} to win (pays 8/5/3/2/1 EP based on card draw order)")
        
        print("\nAvailable race loser bets:")
        start_idx = len(winner_bets)
        for i, (_, camel) in enumerate(loser_bets):
            print(f"{start_idx+i+1}. Bet on {camel} to lose (pays 8/5/3/2/1 EP based on card draw order)")
        
        print(f"{len(winner_bets + loser_bets)+1}. Skip betting")
        
        try:
            choice = int(input("Choose bet (number): ")) - 1
            all_bets = winner_bets + loser_bets
            
            if 0 <= choice < len(all_bets):
                bet_info = all_bets[choice]
                if self.betting_manager.place_bet(player, bet_info):
                    print(f"Placed {bet_info[0]} bet on {bet_info[1]} (card added to deck)")
                    print(f"Finish cards remaining: {player.finish_cards_remaining}")
                    self._record_betting_decision(player, bet_info, 'placed')
                else:
                    print("Unable to place bet! (No finish cards remaining)")
        except (ValueError, IndexError):
            print("Invalid choice, skipping bet")
    
    def _bot_race_betting(self, player, winner_bets, loser_bets):
        """Handle bot player race betting"""
        all_bets = winner_bets + loser_bets
        bet_choice = player.decide_bet(all_bets, self.game)
        
        if bet_choice:
            if self.betting_manager.place_bet(player, bet_choice):
                print(f"{player.name} placed {bet_choice[0]} bet on {bet_choice[1]} (card added to deck)")
                print(f"{player.name} finish cards remaining: {player.finish_cards_remaining}")
                self._record_betting_decision(player, bet_choice, 'placed')
            else:
                print(f"{player.name} unable to place bet (no finish cards)")
        else:
            print(f"{player.name} chose not to bet")
    
    def _betting_phase_leg_bets(self):
        """Handle leg winner betting before each round"""
        if not self.players:
            return
            
        leg_bets = self.betting_manager.get_available_leg_bets(self.game.camels)
        if not leg_bets:
            print("No leg bets available this round")
            return
        
        print(f"\n=== LEG BETTING PHASE - Round {self.current_round + 1} ===")
        
        for player in self.players:
            if player.money <= 0:
                continue
                
            print(f"\n{player.name}'s turn (${player.money})")
            
            if isinstance(player, HumanPlayer):
                self._human_leg_betting(player, leg_bets)
            else:
                self._bot_leg_betting(player, leg_bets)
    
    def _human_leg_betting(self, player, leg_bets):
        """Handle human player leg betting"""
        print("Available leg winner bets:")
        for i, (_, camel, ticket_value) in enumerate(leg_bets):
            print(f"{i+1}. Take {camel} ticket (win {ticket_value} EP if 1st, 1 EP if 2nd, lose 1 EP if 3rd+)")
        print(f"{len(leg_bets)+1}. Skip betting")
        
        try:
            choice = int(input("Choose bet (number): ")) - 1
            if 0 <= choice < len(leg_bets):
                bet_info = leg_bets[choice]
                if self.betting_manager.place_bet(player, bet_info):
                    print(f"Took {bet_info[1]} ticket (value: {bet_info[2]} EP)")
                    self._record_betting_decision(player, bet_info, 'placed')
                    # Remove this bet from available options
                    leg_bets.pop(choice)
                else:
                    print("Unable to take ticket!")
        except (ValueError, IndexError):
            print("Invalid choice, skipping bet")
    
    def _bot_leg_betting(self, player, leg_bets):
        """Handle bot player leg betting"""
        bet_choice = player.decide_bet(leg_bets, self.game)
        
        if bet_choice:
            if self.betting_manager.place_bet(player, bet_choice):
                print(f"{player.name} took {bet_choice[1]} ticket (value: {bet_choice[2]} EP)")
                self._record_betting_decision(player, bet_choice, 'placed')
                # Remove bet from available options
                leg_bets[:] = [bet for bet in leg_bets if not (bet[1] == bet_choice[1])]
            else:
                print(f"{player.name} unable to take ticket")
        else:
            print(f"{player.name} chose not to bet")
    
    def play_round(self):
        """Play a complete leg using turn-based actions"""
        self.current_round += 1
        print(f"\n{'='*20} LEG {self.current_round} {'='*20}")
        
        # Reset dice for new leg
        self.turn_manager.dice.reset()
        self.turn_manager.leg_ended = False
        
        # Display current standings
        self._display_player_standings()
        
        # Play turn-based actions until leg ends
        print("\n=== LEG GAMEPLAY ===")
        winner = self._execute_turn_based_leg()
        
        if winner:
            self.game_finished = True
            self.winner = winner
            self._resolve_game_end()
        else:
            self._resolve_round_end()
        
        return winner
    
    def _execute_turn_based_leg(self):
        """Execute turn-based leg until all 5 dice are rolled"""
        turn_count = 0
        
        while not self.turn_manager.leg_ended and not self.game.board.is_finished():
            turn_count += 1
            current_player = self.turn_manager.get_current_player()
            
            print(f"\n--- Turn {turn_count} ---")
            self.game.board.display_board()
            
            # Process player's turn
            success, message = self.turn_manager.process_player_turn(current_player)
            
            if success:
                print(f"SUCCESS {current_player.name}: {message}")
                # Record action for statistics
                self._record_action(current_player, message)
            else:
                print(f"FAILED {current_player.name}: {message}")
            
            # Check if any camel finished the race (crossed finish line)
            if self.game.board.is_finished():
                winner = self.game.board.get_winning_camel()
                if winner:
                    print(f"RACE FINISHED! {winner.colored_name()} crossed the finish line!")
                    return winner
            
            # Move to next player's turn
            self.turn_manager.next_turn()
            
            # Safety check - prevent infinite loops
            if turn_count > 100:
                print("Maximum turns reached - ending leg")
                break
        
        print(f"Leg ended after {turn_count} turns")
        return None
    
    def _record_action(self, player, action_description):
        """Record player action for statistics"""
        self.game_stats['betting_decisions'].append({
            'round': self.current_round,
            'player': player.name,
            'strategy': getattr(player, 'strategy', 'human'),
            'action': action_description,
            'player_money_before': player.money
        })
    
    def _resolve_round_end(self):
        """Handle end-of-round betting resolution"""
        # Determine leg winner (furthest camel)
        leg_winner = self.game.board.get_winning_camel()
        leg_results = [leg_winner] if leg_winner else []
        
        # Resolve leg winner bets
        resolved_bets = self.betting_manager.resolve_leg_bets(leg_results)
        
        # Apply leg bet payouts
        for bet in resolved_bets:
            if hasattr(bet, 'leg_payout'):
                payout = bet.leg_payout
                for player in self.players:
                    if player.name == bet.player_name:
                        player.receive_payout(payout)
                        if payout > 0:
                            print(f"{player.name} wins {payout} EP from leg bet!")
                        else:
                            print(f"{player.name} loses {abs(payout)} EP from leg bet!")
                        break
        
        # Pay out pyramid tickets (1 EP each from bank)
        for player in self.players:
            if player.pyramid_tickets > 0:
                ticket_count = player.pyramid_tickets
                payout = player.collect_pyramid_payouts()
                self.bank -= payout
                print(f"{player.name} collects {payout} EP from {ticket_count} pyramid tickets!")
        
        # Rotate starting player marker based on last pyramid ticket taker
        if self.turn_manager.last_pyramid_player:
            self.turn_manager.rotate_starting_player_marker(self.turn_manager.last_pyramid_player)
        
        # Reset for next round
        self.betting_manager.reset_leg_tickets()
        self.pyramid_ticket_manager.reset_for_new_leg()
        
        # Clear players' leg bets
        for player in self.players:
            player.clear_leg_bets()
        
        # Reset turn manager for new leg
        self.turn_manager.dice.reset()
        self.turn_manager.leg_ended = False
        self.turn_manager.last_pyramid_player = None
    
    def _resolve_game_end(self):
        """Handle end-of-game betting resolution"""
        print(f"\nGAME OVER! Winner: {self.winner.colored_name()}")
        
        # Get final race positions
        final_positions = self._get_final_race_positions()
        
        # Resolve race winner and loser bets
        resolved_bets = self.betting_manager.resolve_race_bets(final_positions)
        
        # Pay out race bet results
        total_payouts = 0
        for bet in resolved_bets:
            payout = getattr(bet, 'payout', 0)
            if payout != 0:
                for player in self.players:
                    if player.name == bet.player_name:
                        player.receive_payout(payout)
                        if payout > 0:
                            print(f"{player.name} wins {payout} EP from race bet!")
                        else:
                            print(f"{player.name} loses {abs(payout)} EP from race bet!")
                        total_payouts += payout
                        break
        
        # Display final results
        self._display_final_results()
        self._update_game_statistics()
    
    def _get_final_race_positions(self):
        """Get camels in final race order"""
        # Sort all camels by position (furthest first)
        all_camels = [c for c in self.game.camels if not c.moves_backward]
        all_camels.sort(key=lambda c: c.position, reverse=True)
        return all_camels
    
    def _display_player_standings(self):
        """Display current player money and active bets"""
        print("\n=== PLAYER STANDINGS ===")
        for player in self.players:
            active_bets = len(player.get_active_bets())
            print(f"{player.name}: {player.money} EP ({active_bets} active bets, {player.finish_cards_remaining} finish cards, {player.pyramid_tickets} pyramid tickets)")
    
    def _display_final_results(self):
        """Display final game results"""
        print("\n" + "="*40)
        print("FINAL RESULTS")
        print("="*40)
        
        # Sort players by money
        sorted_players = sorted(self.players, key=lambda p: p.money, reverse=True)
        for i, player in enumerate(sorted_players):
            starting = self.game_stats['player_performances'][player.name]['starting_money']
            profit = player.money - starting
            roi = (profit / starting * 100) if starting > 0 else 0
            print(f"{i+1}. {player.name}: {player.money} EP ({profit:+.0f} EP, {roi:+.1f}% ROI)")
    
    def _record_betting_decision(self, player, bet_info, outcome):
        """Record betting decision for analysis"""
        decision = {
            'round': self.current_round,
            'player': player.name,
            'strategy': getattr(player, 'strategy', 'human'),
            'bet_type': bet_info[0],
            'target': bet_info[1],
            'amount': bet_info[2] if len(bet_info) > 2 else 0,
            'outcome': outcome,
            'player_money_before': player.money
        }
        self.game_stats['betting_decisions'].append(decision)
        
        if outcome == 'placed':
            self.game_stats['total_bets_placed'] += 1
            amount = bet_info[2] if len(bet_info) > 2 else 0
            self.game_stats['total_money_wagered'] += amount
            self.game_stats['player_performances'][player.name]['bets_placed'] += 1
    
    def _update_game_statistics(self):
        """Update final game statistics"""
        self.game_stats['rounds_played'] = self.current_round
        
        for player in self.players:
            stats = self.game_stats['player_performances'][player.name]
            stats['final_money'] = player.money
            stats['bets_won'] = len([bet for bet in player.bet_history if bet.resolved and bet.won])
            
            starting = stats['starting_money']
            if starting > 0:
                stats['roi'] = ((player.money - starting) / starting) * 100
    
    def get_game_statistics(self):
        """Return complete game statistics for analysis"""
        return self.game_stats