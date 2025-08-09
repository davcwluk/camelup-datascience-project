# main_with_betting.py

from camelup.game_manager import GameManager
from camelup.player import HumanPlayer, BotPlayer
from camelup.models import Camel
from colorama import init, Fore
from random import shuffle
import random
import os
import platform
from camelup.probability_calculator import ProbabilityCalculator

def clear_screen():
    """Clear the terminal screen for both Windows and Unix-like systems"""
    if platform.system().lower() == "windows":
        os.system('cls')
    else:
        os.system('clear')

def check_winner(game):
    """Check if any colored camel has crossed the finish line"""
    for camel in game.camels:
        # Only check colored camels (not black/white)
        if not camel.moves_backward and camel.position >= 16:
            return camel
    return None

def play_round(game):
    """Handle a single round of dice drawing and movement"""
    available_dice = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'BW']
    dice_rolled = 0
    rolled_dice_history = []
    calculator = ProbabilityCalculator(game)
    
    print("\nPress Enter to draw dice. Need to draw 5 dice to complete the round.")
    while dice_rolled < 5:
        # Display rolled dice history
        display_rolled_dice(game, rolled_dice_history)
        
        # Calculate and show probabilities before each draw
        if len(available_dice) > 1:  # Show probabilities when there are multiple dice left
            print("\nPossible outcomes for next draw:")
            outcomes, probabilities = calculator.calculate_possible_outcomes(available_dice)
            for outcome in outcomes:
                print(outcome)
            
        input(f"\nPress Enter to draw dice ({dice_rolled}/5 drawn)...")
        
        # Randomly select and remove a dice
        selected_dice = random.choice(available_dice)
        available_dice.remove(selected_dice)
        
        if selected_dice == 'BW':
            steps, color = game.dice.roll_bw()
            camel = next(c for c in game.camels if c.name == color)
            rolled_dice_history.append((color, steps))
        else:
            steps = game.dice.roll_colored()
            camel = next(c for c in game.camels if c.name == selected_dice)
            rolled_dice_history.append((selected_dice, steps))
        
        print(f"Drew {camel.colored_name()} dice - rolled {steps}")
        game.board.move_camel_with_stack(camel, steps)
        game.board.display_board()
        
        dice_rolled += 1
        
        # Display final dice history after last dice is rolled
        if dice_rolled == 5:
            display_rolled_dice(game, rolled_dice_history)
        
        # Check for winner after each move
        winner = check_winner(game)
        if winner:
            return winner
            
    print(f"\nRound complete! All {dice_rolled} dice have been rolled.")
    return None

def display_rolled_dice(game, rolled_dice_history):
    """Display the history of rolled dice in a formatted way"""
    if not rolled_dice_history:
        print("No dice rolled yet")
        return
        
    print("\nDice rolled this round:")
    for dice_color, steps in rolled_dice_history:
        camel = next(c for c in game.camels if c.name == dice_color)
        print(f"• {camel.colored_name()} rolled {steps}")

def setup_players():
    """Setup players for the game"""
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

def run_initial_setup(game_manager):
    """Run the initial dice setup phase"""
    game = game_manager.game
    
    print("\nDrawing and rolling dice for initial camel positions...")
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

def main():
    clear_screen()
    # Initialize colorama for color support
    init(autoreset=True)
    
    print("🐪 CAMEL UP - Data Science Edition 🐪")
    print("=====================================")
    
    # Setup players
    players = setup_players()
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
    run_initial_setup(game_manager)
    
    # Main game loop
    print("\n" + "="*50)
    print("STARTING MAIN GAME WITH BETTING!")
    print("="*50)
    
    while not game_manager.game_finished:
        winner = game_manager.play_round()
        
        if winner:
            break
            
        # Check if players want to continue
        if any(isinstance(p, HumanPlayer) for p in players):
            print("\nPress Enter to continue to next round, or 'q' to quit...")
            user_input = input()
            if user_input.lower() == 'q':
                break
    
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