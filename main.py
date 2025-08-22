# main.py

from camelup.game_manager import GameManager
from camelup.player import HumanPlayer, BotPlayer
from camelup.models import Camel
from colorama import init, Fore
from random import shuffle
import random
import os
import platform
import sys
import argparse

def clear_screen():
    """Clear the terminal screen for both Windows and Unix-like systems"""
    if platform.system().lower() == "windows":
        os.system('cls')
    else:
        os.system('clear')


def setup_players(debug_mode=False):
    """Setup players for the game"""
    if debug_mode:
        print("=== DEBUG MODE: Auto-setting players ===")
        players = []
        # Add David as human player
        players.append(HumanPlayer("David"))
        
        # Add 3 bot players with different strategies
        strategies = ['random', 'probability', 'conservative']
        for strategy in strategies:
            name = f"Bot-{strategy.capitalize()}"
            players.append(BotPlayer(name, strategy=strategy))
        
        print(f"Debug setup: David (human) + 3 AI players ({', '.join(strategies)})")
        return players
    
    print("=== PLAYER SETUP ===")
    players = []
    
    # Get number of human players
    while True:
        try:
            num_humans = int(input("Number of human players (0-4): "))
            if 0 <= num_humans <= 4:
                break
            print("Please enter 0-4 players")
        except ValueError:
            print("Please enter a valid number")
    
    # Add human players
    for i in range(num_humans):
        name = input(f"Enter name for player {i+1}: ") or f"Player {i+1}"
        players.append(HumanPlayer(name))
    
    # Get number of bot players
    remaining_slots = 4 - num_humans
    if remaining_slots > 0:
        while True:
            try:
                num_bots = int(input(f"Number of bot players (0-{remaining_slots}): "))
                if 0 <= num_bots <= remaining_slots:
                    break
                print(f"Please enter 0-{remaining_slots} bot players")
            except ValueError:
                print("Please enter a valid number")
        
        # Add bot players with different strategies
        strategies = ['random', 'probability', 'conservative', 'aggressive']
        for i in range(num_bots):
            strategy = strategies[i % len(strategies)]
            name = f"Bot-{strategy.capitalize()}"
            players.append(BotPlayer(name, strategy=strategy))
    
    return players

def initialize_camels():
    """Initialize game camels"""
    camels = [
        # Forward-moving camels
        Camel("Red", Fore.RED),
        Camel("Blue", Fore.BLUE),
        Camel("Green", Fore.GREEN),
        Camel("Yellow", Fore.YELLOW),
        Camel("Purple", Fore.MAGENTA),
        # Backward-moving camels
        Camel("Black", Fore.WHITE, moves_backward=True),  # Using WHITE for visibility
        Camel("White", Fore.LIGHTWHITE_EX, moves_backward=True)
    ]
    return camels

def run_initial_setup(game_manager, debug_mode=False):
    """Run the initial dice setup phase"""
    game = game_manager.game
    
    print("\nDrawing and rolling dice for initial camel positions...")
    if not debug_mode:
        input("Press Enter to start initial setup...")
    
    camel_order = list(game.camels)
    shuffle(camel_order)
    
    # Create a list of all dice to be rolled
    dice_to_roll = []
    
    # Add special dice rolls for black and white
    dice_to_roll.append(('White', game.dice.roll_special_initial()))
    dice_to_roll.append(('Black', game.dice.roll_special_initial()))
    
    # Add colored dice rolls
    for camel in camel_order:
        if camel.name not in ['Black', 'White']:
            dice_to_roll.append((camel.name, game.dice.roll_colored()))
    
    # Shuffle the dice rolls
    random.shuffle(dice_to_roll)
    
    # Process all dice rolls in random order
    for dice_color, steps in dice_to_roll:
        camel = next(c for c in game.camels if c.name == dice_color)
        game.board.move_camel_initial_setup(camel, steps)
        direction = "backward" if camel.moves_backward else "forward"
        print(f"Drew {camel.colored_name()} dice - moves {steps} steps {direction}")
        game.board.display_board()
    
    print("\nInitial positions set! Starting main game...")
    game.board.display_board()

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Camel Up - Data Science Edition")
    parser.add_argument('-debug', '--debug', action='store_true', 
                       help='Run in debug mode with auto-setup (David + 3 AI players)')
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    clear_screen()
    # Initialize colorama for color support
    init(autoreset=True)
    
    if args.debug:
        print("CAMEL UP - Data Science Edition (DEBUG MODE)")
    else:
        print("CAMEL UP - Data Science Edition")
    print("=====================================")
    
    # Setup players
    players = setup_players(debug_mode=args.debug)
    if not players:
        print("No players selected. Exiting...")
        return
    
    # Create game manager
    game_manager = GameManager(players)
    
    # Initialize camels
    camels = initialize_camels()
    
    # Initialize game and handle initial betting
    game_manager.initialize_game(camels)
    
    # Display initial board
    print("\nInitial board state:")
    game_manager.game.board.display_board()
    
    # Run initial camel positioning
    run_initial_setup(game_manager, debug_mode=args.debug)
    
    # Main game loop
    print("\n" + "="*50)
    print("STARTING MAIN GAME WITH BETTING!")
    print("="*50)
    
    while not game_manager.game_finished:
        winner = game_manager.play_round()
        
        if winner:
            break
            
        # Check if players want to continue
        if any(isinstance(p, HumanPlayer) for p in players) and not args.debug:
            print("\nPress Enter to continue to next round, or 'q' to quit...")
            user_input = input()
            if user_input.lower() == 'q':
                break
        elif args.debug:
            print("\n[DEBUG MODE: Auto-continuing to next round...]")
    
    # Display final statistics
    stats = game_manager.get_game_statistics()
    print("\n" + "="*50)
    print("GAME STATISTICS")
    print("="*50)
    print(f"Rounds played: {stats['rounds_played']}")
    print(f"Total bets placed: {stats['total_bets_placed']}")
    print(f"Total money wagered: ${stats['total_money_wagered']}")
    
    print("\nThanks for playing!")

if __name__ == "__main__":
    main()