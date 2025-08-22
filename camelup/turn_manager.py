# turn_manager.py

from .dice import Dice
from .probability_calculator import ProbabilityCalculator
import random
import sys

class TurnManager:
    """Manages turn-based gameplay with 4 player actions"""
    
    def __init__(self, players, game, betting_manager, spectator_tile_manager, pyramid_ticket_manager, game_manager=None):
        self.players = players
        self.game = game
        self.betting_manager = betting_manager
        self.spectator_tile_manager = spectator_tile_manager
        self.pyramid_ticket_manager = pyramid_ticket_manager
        self.game_manager = game_manager  # For accessing bank
        self.dice = Dice()
        self.probability_calculator = ProbabilityCalculator(game)
        self.leg_ended = False
        self.last_pyramid_player = None  # Track who took the last pyramid ticket
        self.leg_dice_history = []  # Track dice rolled this leg
        
        # Determine starting player (youngest player according to rulebook)
        self.starting_player_index = self._determine_starting_player()
        self.current_player_index = self.starting_player_index
        
    def get_current_player(self):
        """Get the current player whose turn it is"""
        return self.players[self.current_player_index]
    
    def _determine_starting_player(self):
        """Determine the starting player (youngest player according to rulebook)"""
        # For simplicity in simulation, we'll use the first player
        # In a real game, this would ask for ages and find youngest
        print(f"Starting player: {self.players[0].name} (youngest player)")
        return 0
    
    def next_turn(self):
        """Move to next player's turn"""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
    
    def reset_to_starting_player(self):
        """Reset turn to starting player for new leg"""
        self.current_player_index = self.starting_player_index
    
    def rotate_starting_player_marker(self, last_pyramid_player_name):
        """Move starting player marker to the left of the player who took the last pyramid ticket"""
        # Find the player who took the last pyramid ticket
        last_player_index = None
        for i, player in enumerate(self.players):
            if player.name == last_pyramid_player_name:
                last_player_index = i
                break
        
        if last_player_index is not None:
            # Starting player marker goes to the player to the left (previous in turn order)
            self.starting_player_index = (last_player_index - 1) % len(self.players)
            new_starting_player = self.players[self.starting_player_index]
            print(f"Starting player marker moves to {new_starting_player.name}")
        
        # Reset current player to new starting player for next leg
        self.current_player_index = self.starting_player_index
    
    def get_available_actions(self, player):
        """Get all available actions for the current player"""
        actions = []
        
        # Action 1: Take leg winner betting ticket
        leg_bets = self.betting_manager.get_available_leg_bets(self.game.camels)
        if leg_bets:
            actions.append({
                'id': 1,
                'name': 'Take Leg Winner Ticket',
                'description': 'Take a betting ticket for leg winner',
                'available_bets': leg_bets
            })
        
        # Action 2: Place/move spectator tile
        available_positions = self.spectator_tile_manager.get_available_positions(self.game.board)
        existing_tile_pos = self.spectator_tile_manager.get_player_tile_position(player.name)
        
        if available_positions or existing_tile_pos is not None:
            action_name = 'Move Spectator Tile' if existing_tile_pos is not None else 'Place Spectator Tile'
            description = 'Move your spectator tile to a different position' if existing_tile_pos is not None else 'Place a spectator tile on the board (+1 or -1 movement)'
            
            actions.append({
                'id': 2,
                'name': action_name,
                'description': description,
                'available_positions': available_positions,
                'existing_tile_position': existing_tile_pos
            })
        
        # Action 3: Take pyramid ticket (move camel immediately)
        if self.pyramid_ticket_manager.can_take_ticket():
            actions.append({
                'id': 3,
                'name': 'Take Pyramid Ticket',
                'description': 'Take pyramid ticket, roll dice, move a camel immediately, gain 1 EP at leg end'
            })
        
        # Action 4: Take race winner/loser card
        if player.can_place_race_bet():
            race_winner_bets = self.betting_manager.get_available_race_bets(self.game.camels)
            race_loser_bets = self.betting_manager.get_available_race_loser_bets(self.game.camels)
            if race_winner_bets or race_loser_bets:
                actions.append({
                    'id': 4,
                    'name': 'Take Race Card',
                    'description': 'Place race winner or race loser card',
                    'winner_bets': race_winner_bets,
                    'loser_bets': race_loser_bets
                })
        
        return actions
    
    def execute_action_1(self, player, bet_choice):
        """Execute Action 1: Take leg winner betting ticket"""
        success = self.betting_manager.place_bet(player, bet_choice)
        if success:
            print(f"{player.name} took {bet_choice[1]} ticket (value: {bet_choice[2]} EP)")
            return True, f"Took {bet_choice[1]} ticket"
        return False, "Unable to take ticket"
    
    def execute_action_2(self, player, position, side='cheering'):
        """Execute Action 2: Place or move spectator tile"""
        existing_pos = self.spectator_tile_manager.get_player_tile_position(player.name)
        
        if existing_pos is not None:
            # Player is moving an existing tile
            success = self.spectator_tile_manager.move_tile(player.name, position, side)
            if success:
                symbol = "+" if side == 'cheering' else "-"
                print(f"{player.name} moved {side} tile {symbol} from position {existing_pos} to {position}")
                return True, f"Moved {side} tile from {existing_pos} to {position}"
            return False, "Unable to move tile"
        else:
            # Player is placing a new tile
            success = self.spectator_tile_manager.place_tile(player.name, position, side)
            if success:
                symbol = "+" if side == 'cheering' else "-"
                print(f"{player.name} placed {side} tile {symbol} at position {position}")
                return True, f"Placed {side} tile at position {position}"
            return False, "Unable to place tile"
    
    def execute_action_3(self, player):
        """Execute Action 3: Take pyramid ticket and move camel"""
        # Take pyramid ticket
        ticket = self.pyramid_ticket_manager.take_ticket(player.name)
        if not ticket:
            return False, "No pyramid tickets available"
        
        player.add_pyramid_ticket()
        # NOTE: According to rulebook, players only get 1 EP per ticket at END of leg, not immediately
        
        # Track this player as the last pyramid ticket taker
        self.last_pyramid_player = player.name
        
        # Get available dice for rolling
        available_dice_colors = self.dice.get_available_dice()
        
        # Roll dice to move a camel
        dice_result = self.dice.roll_random_die()
        if not dice_result:
            return False, "No dice available to roll"
        
        die_color, steps = dice_result
        print(f"\n{player.name} took pyramid ticket and rolled {die_color} die: {steps}")
        
        # Add to dice history for this leg
        self.leg_dice_history.append((die_color, steps))
        
        # Find the camel to move
        camel_to_move = None
        for camel in self.game.camels:
            if camel.name == die_color:
                camel_to_move = camel
                break
        
        if camel_to_move:
            # Move the camel and its stack
            old_position = camel_to_move.position
            spectator_payout = self.game.board.move_camel_with_stack(camel_to_move, steps)
            new_position = camel_to_move.position
            
            print(f"{camel_to_move.colored_name()} moved from position {old_position} to {new_position}")
            
            # Display updated board
            print(f"\n=== UPDATED BOARD ===")
            self.game.board.display_board()
            
            # Display dice rolled this leg
            self._display_leg_dice_history()
            
            # Handle spectator tile payout from bank
            if spectator_payout:
                tile_owner, payout = spectator_payout
                for p in self.players:
                    if p.name == tile_owner:
                        p.receive_payout(payout)
                        if self.game_manager:
                            self.game_manager.bank -= payout
                        print(f"{tile_owner} receives {payout} EP from spectator tile (bank pays)!")
                        break
            
            # Check if leg ended (all 6 dice have been rolled - 5 colored + 1 BW)
            if len(self.dice.used_dice) == 6:
                self.leg_ended = True
                print("\nLEG ENDED: All dice have been rolled - leg ends!")
            
            return True, f"Took pyramid ticket, moved {die_color} camel {steps} steps (1 EP at leg end)"
        
        return False, f"Could not find camel for {die_color} die"
    
    def execute_action_4(self, player, bet_choice):
        """Execute Action 4: Take race winner/loser card"""
        success = self.betting_manager.place_bet(player, bet_choice)
        if success:
            bet_type = bet_choice[0].replace('_', ' ')
            print(f"{player.name} placed {bet_type} bet on {bet_choice[1]}")
            print(f"Finish cards remaining: {player.finish_cards_remaining}")
            return True, f"Placed {bet_type} bet on {bet_choice[1]}"
        return False, "Unable to place race bet"
    
    def display_turn_options(self, player):
        """Display available actions for player's turn"""
        print(f"\n{player.name}'s turn ({player.money} EP, {player.finish_cards_remaining} finish cards, {player.pyramid_tickets} pyramid tickets)")
        
        actions = self.get_available_actions(player)
        if not actions:
            print("No actions available - skipping turn")
            return []
        
        # Show probability analysis if Action 3 (pyramid ticket) is available
        pyramid_action_available = any(action['id'] == 3 for action in actions)
        if pyramid_action_available:
            available_dice_colors = self.dice.get_available_dice()
            if available_dice_colors:  # Show probabilities if any dice are available
                print(f"\n=== PROBABILITY ANALYSIS (if you take pyramid ticket) ===")
                print(f"Available dice: {available_dice_colors}")
                self._display_dice_probabilities(available_dice_colors)
                print("=" * 60)
        
        print("Available actions:")
        for action in actions:
            print(f"{action['id']}. {action['name']} - {action['description']}")
        
        return actions
    
    def process_player_turn(self, player):
        """Process a complete player turn"""
        actions = self.display_turn_options(player)
        
        if not actions:
            return False, "No actions available"
        
        # For human players, get input
        if hasattr(player, 'strategy'):  # Bot player
            return self._process_bot_turn(player, actions)
        else:  # Human player
            return self._process_human_turn(player, actions)
    
    def _process_human_turn(self, player, actions):
        """Process human player turn with input"""
        try:
            choice = int(input("Choose action (number): "))
            selected_action = None
            for action in actions:
                if action['id'] == choice:
                    selected_action = action
                    break
            
            if not selected_action:
                return False, "Invalid action choice"
            
            return self._execute_selected_action(player, selected_action)
            
        except ValueError:
            return False, "Invalid input"
        except KeyboardInterrupt:
            print("\nGame interrupted by user. Exiting...")
            sys.exit(0)
    
    def _process_bot_turn(self, player, actions):
        """Process bot player turn automatically"""
        # Simple bot strategy: choose first available action
        selected_action = actions[0]
        return self._execute_selected_action(player, selected_action)
    
    def _execute_selected_action(self, player, action):
        """Execute the selected action"""
        action_id = action['id']
        
        if action_id == 1:  # Leg winner ticket
            if hasattr(player, 'strategy'):  # Bot
                bet_choice = action['available_bets'][0]  # Take first available
            else:  # Human
                bet_choice = self._get_leg_bet_choice(action['available_bets'])
                if not bet_choice:
                    return False, "No bet selected"
            
            return self.execute_action_1(player, bet_choice)
        
        elif action_id == 2:  # Spectator tile
            if hasattr(player, 'strategy'):  # Bot
                position = action['available_positions'][0]
                side = random.choice(['cheering', 'booing'])
            else:  # Human
                position, side = self._get_spectator_tile_choice(action['available_positions'])
                if position is None:
                    return False, "No tile placement selected"
            
            return self.execute_action_2(player, position, side)
        
        elif action_id == 3:  # Pyramid ticket
            return self.execute_action_3(player)
        
        elif action_id == 4:  # Race card
            if hasattr(player, 'strategy'):  # Bot
                all_bets = action['winner_bets'] + action['loser_bets']
                bet_choice = random.choice(all_bets)
            else:  # Human
                bet_choice = self._get_race_bet_choice(action['winner_bets'], action['loser_bets'])
                if not bet_choice:
                    return False, "No bet selected"
            
            return self.execute_action_4(player, bet_choice)
        
        return False, "Unknown action"
    
    def _get_leg_bet_choice(self, available_bets):
        """Get human player's leg bet choice"""
        print("Available leg winner bets:")
        for i, (_, camel, ticket_value) in enumerate(available_bets):
            print(f"{i+1}. {camel} ticket (value: {ticket_value} EP)")
        
        try:
            choice = int(input("Choose bet (number): ")) - 1
            if 0 <= choice < len(available_bets):
                return available_bets[choice]
        except ValueError:
            pass
        except KeyboardInterrupt:
            print("\nGame interrupted by user. Exiting...")
            sys.exit(0)
        return None
    
    def _get_spectator_tile_choice(self, available_positions):
        """Get human player's spectator tile choice"""
        print(f"Available positions: {available_positions}")
        print("1. Cheering tile (+1 movement)")
        print("2. Booing tile (-1 movement)")
        
        try:
            position = int(input("Choose position: "))
            if position in available_positions:
                side_choice = int(input("Choose tile type (1=cheering, 2=booing): "))
                side = 'cheering' if side_choice == 1 else 'booing'
                return position, side
        except ValueError:
            pass
        except KeyboardInterrupt:
            print("\nGame interrupted by user. Exiting...")
            sys.exit(0)
        return None, None
    
    def _get_race_bet_choice(self, winner_bets, loser_bets):
        """Get human player's race bet choice"""
        print("Available race bets:")
        all_bets = winner_bets + loser_bets
        for i, bet in enumerate(all_bets):
            bet_type = bet[0].replace('_', ' ')
            print(f"{i+1}. {bet_type} on {bet[1]}")
        
        try:
            choice = int(input("Choose bet (number): ")) - 1
            if 0 <= choice < len(all_bets):
                return all_bets[choice]
        except ValueError:
            pass
        except KeyboardInterrupt:
            print("\nGame interrupted by user. Exiting...")
            sys.exit(0)
        return None
    
    def _display_dice_probabilities(self, available_dice_colors):
        """Display probability calculations for available dice"""
        outcomes, leading_counts = self.probability_calculator.calculate_possible_outcomes(available_dice_colors)
        for outcome in outcomes:
            print(outcome)
    
    def _display_leg_dice_history(self):
        """Display the history of dice rolled this leg"""
        if not self.leg_dice_history:
            print("\nNo dice rolled yet this leg")
            return
        
        print(f"\nDice rolled this leg:")
        for dice_color, steps in self.leg_dice_history:
            camel = next(c for c in self.game.camels if c.name == dice_color)
            print(f"• {camel.colored_name()} rolled {steps}")
        
        dice_remaining = 5 - len(self.leg_dice_history)
        if dice_remaining > 0:
            print(f"Dice remaining in pyramid: {dice_remaining}")
        else:
            print("All dice have been rolled - leg complete")