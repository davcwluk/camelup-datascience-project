#!/usr/bin/env python3
# analyze_ev.py - Analyze expected values of different strategies in Camel Up

import random
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
from copy import deepcopy
from collections import defaultdict
from colorama import init, Fore

from camelup.game import CamelUpGame
from camelup.models import Camel
from camelup.probability_calculator import ProbabilityCalculator
from camelup.ev_calculator import ExpectedValueCalculator

# Set up colorama for colored output
init(autoreset=True)

def setup_game():
    """Set up a Camel Up game with standard configuration."""
    # Create game with 7 camels
    game = CamelUpGame(num_camels=7, track_length=16)
    
    # Add the camels
    game.camels = [
        # Forward-moving camels
        Camel("Red", Fore.RED),
        Camel("Blue", Fore.BLUE),
        Camel("Green", Fore.GREEN),
        Camel("Yellow", Fore.YELLOW),
        Camel("Purple", Fore.MAGENTA),
        # Backward-moving camels
        Camel("Black", Fore.WHITE, moves_backward=True),
        Camel("White", Fore.LIGHTWHITE_EX, moves_backward=True)
    ]
    
    # Initialize board with all camels
    game.board.initialize_camels(game.camels)
    
    # Perform initial setup for camel positions
    dice_to_roll = [
        ('White', game.dice.roll_special_initial()),
        ('Black', game.dice.roll_special_initial())
    ]
    
    for camel in game.camels:
        if camel.name not in ['Black', 'White']:
            dice_to_roll.append((camel.name, game.dice.roll_colored()))
    
    # Process all dice rolls
    for dice_color, steps in dice_to_roll:
        camel = next(c for c in game.camels if c.name == dice_color)
        game.board.move_camel_initial_setup(camel, steps)
    
    return game

def analyze_betting_ticket_strategy():
    """Analyze the betting ticket strategy and its expected values over multiple legs."""
    # Set up the game
    game = setup_game()
    ev_calculator = ExpectedValueCalculator(game)
    
    print("Initial board state:")
    game.board.display_board()
    
    # Calculate EVs for betting tickets in the current state
    betting_evs = ev_calculator.calculate_leg_bet_evs(num_simulations=1000)
    print("\nExpected values for betting tickets (Leg 1):")
    
    table_data = []
    for camel_name, ev in sorted(betting_evs.items(), key=lambda x: x[1], reverse=True):
        camel_obj = next(c for c in game.camels if c.name == camel_name)
        tickets_left = ev_calculator.remaining_tickets[camel_name]
        next_position = ev_calculator.ticket_positions[camel_name] + 1
        
        # Calculate payouts for each ticket position
        position_payouts = {1: 5, 2: 3, 3: 2, 4: 1}
        payout = position_payouts.get(next_position, 0) if next_position <= 4 else 0
        
        table_data.append([
            camel_obj.colored_name(), 
            f"{ev:.2f}", 
            f"{tickets_left}",
            f"#{next_position}",
            f"{payout}" if next_position <= 4 else "N/A"
        ])
    
    print(tabulate(table_data, headers=["Camel", "Expected Value", "Tickets Left", "Next Ticket", "Payout if 1st"], tablefmt="pretty"))
    
    # Explain the betting ticket mechanics
    print("\nBetting Ticket Mechanics:")
    print("1. Only the camel that finishes in 1st place pays out")
    print("2. Payout depends on which ticket number you get:")
    print("   - 1st ticket: 5 gold")
    print("   - 2nd ticket: 3 gold")
    print("   - 3rd ticket: 2 gold")
    print("   - 4th ticket: 1 gold")
    print("3. If the camel doesn't finish 1st, you get 0 coins")
    
    # Analyze optimal betting strategy for a single leg
    print("\nOptimal betting strategy for current leg:")
    
    # Take tickets in order of highest EV until all valuable bets are exhausted
    tickets_taken = []
    while True:
        # Recalculate EVs with current ticket availability
        betting_evs = {camel: ev for camel, ev in ev_calculator.calculate_leg_bet_evs().items() 
                      if ev_calculator.remaining_tickets.get(camel, 0) > 0}
        
        if not betting_evs or max(betting_evs.values()) <= 1.0:
            # Stop if no more tickets or pyramid ticket becomes better
            break
            
        best_camel, best_ev = max(betting_evs.items(), key=lambda x: x[1])
        # Get position before taking ticket
        ticket_position = ev_calculator.ticket_positions[best_camel] + 1
        ev_calculator.take_betting_ticket(best_camel)
        camel_obj = next(c for c in game.camels if c.name == best_camel)
        tickets_taken.append((camel_obj.colored_name(), best_ev, ticket_position))
    
    # Display optimal ticket selection
    if tickets_taken:
        print("Best betting tickets to take (in order):")
        for i, (camel, ev, position) in enumerate(tickets_taken, 1):
            position_str = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}.get(position, f"{position}th")
            print(f"{i}. {camel} - {position_str} ticket (EV: {ev:.2f})")
    else:
        print("Taking the pyramid ticket (EV: 1.0) is better than any betting ticket.")
    
    # Compare to pyramid ticket EV
    print("\nComparison with pyramid ticket (EV = 1.0):")
    if tickets_taken:
        avg_ev = sum(ev for _, ev, _ in tickets_taken) / len(tickets_taken)
        improvement = (avg_ev - 1.0) / 1.0 * 100
        print(f"Average EV of best betting tickets: {avg_ev:.2f}")
        print(f"Improvement over pyramid ticket: {improvement:.1f}%")
    
    # Demonstrate the betting ticket mechanics with a simulation
    print("\nDemonstrating betting ticket mechanics with a simulation:")
    
    # Set up a test scenario
    test_game = setup_game()
    test_calculator = ExpectedValueCalculator(test_game)
    
    # Take multiple tickets for the same camel to demonstrate position-based payouts
    # For this example, let's take all 4 tickets for the camel in the lead
    leading_camel = test_game.board.get_leading_camel()
    if leading_camel:
        camel_name = leading_camel.name
        print(f"\nTaking all 4 tickets for {leading_camel.colored_name()} to demonstrate position-based payouts:")
        
        for i in range(4):
            position = test_calculator.ticket_positions[camel_name] + 1
            test_calculator.take_betting_ticket(camel_name)
            position_str = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}.get(position, f"{position}th")
            payout = {1: 5, 2: 3, 3: 2, 4: 1}.get(position, 0)
            print(f"Ticket {position} ({position_str}): Pays {payout} gold if {leading_camel.colored_name()} finishes 1st")
    
        # Simulate the completion of the leg
        print("\nSimulating completion of current leg...")
        game_copy = deepcopy(test_game)
        available_dice = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'BW']
        available_dice = [d for d in available_dice if d not in game_copy.moved_this_leg]
        dice_rolled = 0
        
        # Roll all remaining dice to complete the leg
        while dice_rolled < len(available_dice):
            if not available_dice:
                break
                
            selected_dice = random.choice(available_dice)
            available_dice.remove(selected_dice)
            
            if selected_dice == 'BW':
                steps, color = game_copy.dice.roll_bw()
                move_camel = next(c for c in game_copy.camels if c.name == color)
            else:
                steps = game_copy.dice.roll_colored()
                move_camel = next(c for c in game_copy.camels if c.name == selected_dice)
                
            game_copy.board.move_camel_with_stack(move_camel, steps)
            game_copy.moved_this_leg.add(selected_dice)
            dice_rolled += 1
            
            print(f"Drew {move_camel.colored_name()} dice, rolled {steps}")
        
        game_copy.board.display_board()
        
        # Display final leg results and payouts
        ranking = []
        for pos in range(game_copy.board.track_length, -1, -1):
            for c in reversed(game_copy.board.tiles[pos]):
                if not c.moves_backward:
                    ranking.append(c)
        
        print("\nFinal leg results:")
        for i, camel in enumerate(ranking):
            position_str = {0: "1st", 1: "2nd", 2: "3rd"}.get(i, f"{i+1}th")
            print(f"{position_str}: {camel.colored_name()}")
        
        # Show payouts for each ticket
        print("\nPayouts for betting tickets:")
        if ranking and ranking[0].name == camel_name:
            # The camel won - show payouts for each ticket
            for i in range(1, 5):
                payout = {1: 5, 2: 3, 3: 2, 4: 1}.get(i, 0)
                print(f"Ticket #{i} for {leading_camel.colored_name()}: {payout} gold")
        else:
            # The camel didn't win - all tickets pay 0
            print(f"All tickets for {leading_camel.colored_name()} pay 0 gold (didn't finish 1st)")
    
    # Plot the EVs with detailed ticket information
    plot_betting_evs(betting_evs, ev_calculator)

def compare_strategies():
    """Compare random betting vs. optimal betting strategies."""
    # Set up the game
    game = setup_game()
    game.board.display_board()
    
    # Initialize calculator
    calculator = ProbabilityCalculator(game)
    ev_calculator = ExpectedValueCalculator(game)
    
    # Get camels (exclude backward-moving ones)
    camels = [c for c in game.camels if not c.moves_backward]
    
    # Calculate EVs for all possible actions
    action_evs = ev_calculator.calculate_action_evs(num_simulations=500)
    
    # Find the best action
    best_action = max(action_evs.items(), key=lambda x: x[1])
    random_ev = sum(action_evs.values()) / len(action_evs)
    
    # Compare random vs. optimal strategy
    print("\nStrategy Comparison:")
    data = [
        ["Random Action", f"{random_ev:.2f}"],
        ["Optimal Action", f"{best_action[1]:.2f}"],
        ["Difference", f"{best_action[1] - random_ev:.2f}"],
        ["Improvement", f"{(best_action[1] - random_ev) / random_ev * 100:.1f}%"]
    ]
    print(tabulate(data, headers=["Strategy", "Expected Value"], tablefmt="pretty"))
    
    # Display all available actions
    print("\nAll Available Actions:")
    for action, ev in sorted(action_evs.items(), key=lambda x: x[1], reverse=True):
        print(f"• {action}: EV = {ev:.2f}")
    
    # Calculate leg win probabilities
    print("\nLeg Win Probabilities:")
    available_dice = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'BW']
    available_dice = [d for d in available_dice if d not in game.moved_this_leg]
    outcomes, probabilities = calculator.calculate_possible_outcomes(available_dice)
    
    # Print the outcomes and probability information
    for outcome in outcomes:
        print(outcome)

def plot_betting_evs(betting_evs, ev_calculator):
    """Create a bar chart of the expected values for betting tickets."""
    camels = list(betting_evs.keys())
    evs = list(betting_evs.values())
    
    # Sort by EV
    sorted_indices = np.argsort(evs)[::-1]  # Reverse to get descending order
    camels = [camels[i] for i in sorted_indices]
    evs = [evs[i] for i in sorted_indices]
    
    # Get ticket positions
    positions = [ev_calculator.ticket_positions[camel] + 1 for camel in camels]
    
    # Map camel names to colors for the bars
    camel_colors = {'Red': 'red', 'Blue': 'blue', 'Green': 'green', 
                   'Yellow': 'yellow', 'Purple': 'purple'}
    bar_colors = [camel_colors.get(camel, 'gray') for camel in camels]
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Add horizontal line for pyramid ticket EV (1.0)
    ax.axhline(y=1.0, color='r', linestyle='--', alpha=0.7, label='Take Pyramid Ticket (EV=1.0)')
    
    # Add bars
    bars = ax.bar(camels, evs, color=bar_colors)
    
    # Add labels and title
    ax.set_xlabel('Camels')
    ax.set_ylabel('Expected Value')
    ax.set_title('Expected Value of Betting Tickets for Each Camel (Next Available Ticket)')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        # Add the EV value
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'EV: {height:.2f}', ha='center', va='bottom')
        # Add the ticket position
        position = positions[i]
        position_str = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}.get(position, f"{position}th")
        ax.text(bar.get_x() + bar.get_width()/2., height/2,
                f'Ticket: {position_str}', ha='center', va='center', color='white', fontweight='bold')
        
        # Add the potential payout if camel finishes 1st
        position_payouts = {1: 5, 2: 3, 3: 2, 4: 1}
        payout = position_payouts.get(position, 0) if position <= 4 else 0
        payout_text = f'Payout: {payout}' if position <= 4 else 'No payout'
        ax.text(bar.get_x() + bar.get_width()/2., height/4,
                payout_text, ha='center', va='center', color='white')
    
    ax.legend()
    
    # Add explanatory note
    fig.text(0.5, 0.01, 
             "Note: Payouts are only received if the camel finishes in 1st place.\nPayouts depend on ticket position: 1st=5, 2nd=3, 3rd=2, 4th=1", 
             ha='center', fontsize=10)
    
    # Save the plot
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])  # Adjust layout to make room for the note
    plt.savefig('betting_ticket_ev.png')
    print("\nPlot saved as 'betting_ticket_ev.png'")

if __name__ == "__main__":
    print("Camel Up Expected Value Analysis")
    print("===============================")
    print("1. Analyze Betting Ticket Strategy")
    print("2. Compare All Strategies")
    
    choice = input("\nSelect an option (1-2): ")
    
    if choice == "1":
        analyze_betting_ticket_strategy()
    else:
        compare_strategies() 