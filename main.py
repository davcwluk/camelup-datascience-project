# main.py

from camelup.game import CamelUpGame
from camelup.models import Camel
from colorama import init, Fore
from random import shuffle

def main():
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
    for camel in camel_order:
        steps = game.dice.roll()
        game.board.move_camel_initial_setup(camel, steps)
        direction = "backward" if camel.moves_backward else "forward"
        print(f"Drew {camel.colored_name()} dice - moves {steps} steps {direction}")
        game.board.display_board()
    
    print("\nAll dice drawn and rolled. Initial positions set:")
    game.board.display_board()

    # Continue with the regular game
    while not game.is_race_finished():
        result = game.roll_die_and_move()
        if not result:
            print("\nAll camels have moved this leg.")
            game.reset_leg()
            print("\nNext leg begins:")
            game.board.display_board()
            continue

        camel, steps = result
        print(f"\n{camel.colored_name()} moved {steps} steps.")
        game.board.display_board()

        if game.is_race_finished():
            winner = game.get_winner()
            if winner:
                print(f"\nThe winner is {winner.colored_name()}!")
            else:
                print("\nNo winner determined.")
            break

    if not game.is_race_finished():
        print("\nRace not finished yet!")

if __name__ == "__main__":
    main()
