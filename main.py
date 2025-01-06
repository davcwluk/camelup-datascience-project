# main.py

from camelup.game import CamelUpGame
from camelup.models import Camel
from colorama import init, Fore
from random import shuffle
import random
import os
import platform

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
    # Track available and used dice
    available_dice = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'BW']
    dice_rolled = 0
    
    print("\nPress Enter to draw dice. Need to draw 5 dice to complete the round.")
    while dice_rolled < 5:  # Continue until 5 dice have been rolled
        input(f"\nPress Enter to draw dice ({dice_rolled}/5 drawn)...")
        
        # Randomly select and remove a dice
        selected_dice = random.choice(available_dice)
        available_dice.remove(selected_dice)
        
        if selected_dice == 'BW':
            steps, color = game.dice.roll_bw()
            camel = next(c for c in game.camels if c.name == color)
        else:
            steps = game.dice.roll_colored()
            camel = next(c for c in game.camels if c.name == selected_dice)
        
        print(f"Drew {camel.colored_name()} dice - rolled {steps}")
        game.board.move_camel_with_stack(camel, steps)
        game.board.display_board()
        
        # Check for winner after each move
        winner = check_winner(game)
        if winner:
            return winner
            
        dice_rolled += 1
            
    print(f"\nRound complete! All {dice_rolled} dice have been rolled.")
    return None

def main():
    clear_screen()  # Clear screen at start
    # Initialize colorama for color support
    init(autoreset=True)

    # Create game with 7 camels (5 forward + 2 backward)
    game = CamelUpGame(num_camels=7, track_length=16)
    
    # Add the backward-moving camels
    game.camels = [
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
    
    # Initialize board with all camels
    game.board.initialize_camels(game.camels)

    print("Starting Camel Up Game!\n")
    game.board.display_board()

    input("\nPress Enter to draw and roll dice from the bag...")
    
    camel_order = list(game.camels)
    shuffle(camel_order)
    
    print("\nDrawing and rolling dice from the bag...")
    
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
    
    print("\nAll dice drawn and rolled. Initial positions set:")
    game.board.display_board()

    # After initial setup is complete
    print("\nStarting main game phase!")
    
    round_number = 1
    while True:
        print(f"\n=== Round {round_number} ===")
        winner = play_round(game)
        
        if winner:
            print("\n🏆 GAME OVER! 🏆")
            print(f"\nThe winner is {winner.colored_name()}!")
            game.board.display_board()
            break
            
        print("\nPress Enter to start next round, or type 'q' to quit...")
        user_input = input()
        if user_input.lower() == 'q':
            break
            
        round_number += 1
        
    print("\nThanks for playing!")

if __name__ == "__main__":
    main()
