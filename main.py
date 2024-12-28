# main.py

from camelup.game import CamelUpGame
from colorama import init

def main():
    # Initialize colorama for color support
    init(autoreset=True)

    # Initialize the Camel Up game with default parameters
    game = CamelUpGame(num_camels=5, track_length=16)

    print("Starting Camel Up Game!\n")
    game.board.display_board()

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
