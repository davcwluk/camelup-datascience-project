# Camel Up Game Simulator

This Python-based simulation of the Camel Up board game recreates its core mechanics, dynamically visualizes board states, and provides probabilistic guidance for strategic decision-making, with the aim of modeling diverse betting strategies and running extensive simulations to assess whether outcomes mainly hinge on random factors or if skillful play can yield a discernible edge. Through data-driven methods and systematic experimentation, this project seeks to clarify the game's balance between chance and strategy, highlighting any meaningful predictive elements.

## Key Features

- Complete simulation of Camel Up game mechanics
- Monte Carlo simulation for calculating probabilities and expected values
- Analysis of various player actions and betting strategies 
- Visualization of expected values for different actions

## Installation

1. Clone the repository:

```bash
git clone https://github.com/davcwluk/camelup.git
```

2. Navigate to the project directory:

```bash
cd camelup
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Game Simulation

```bash
python main.py
```

This will start a text-based game simulation that shows probabilities and expected values during gameplay.

### Analyzing Expected Values

```bash
python analyze_ev.py
```

This script analyzes the expected values of different actions and compares random vs. optimal strategies. It helps determine whether the game is primarily chance-based or if skilled play provides an advantage.

## Expected Value Analysis Approach

The project uses two main approaches to determine if Camel Up is primarily a game of chance or skill:

1. **Expected Value (EV) Calculation**: We calculate the expected monetary return for each possible action using Monte Carlo simulations.

2. **Strategy Comparison**: We compare the expected values of:
   - Random strategy (selecting actions randomly)
   - Optimal strategy (always selecting the highest EV action)

If the difference between random and optimal play is significant, this suggests skill plays an important role in success. If the difference is minimal, the game is more chance-based.

### Player Actions and Their EV Calculations

1. **Take Pyramid Ticket**: This action always yields exactly 1 coin (EV = 1.0).

2. **Take Betting Ticket**: Betting on which camel will finish in 1st place at the end of the leg.
   - Each camel has only 4 betting tickets available
   - Payouts are based on the order in which tickets were taken, not the camel's final position:
     - 1st ticket taken: 5 coins (if the camel finishes 1st)
     - 2nd ticket taken: 3 coins (if the camel finishes 1st)
     - 3rd ticket taken: 2 coins (if the camel finishes 1st) 
     - 4th ticket taken: 1 coin (if the camel finishes 1st)
   - You only receive a payout if the camel finishes in 1st place; otherwise, you get 0 coins
   - The EV is calculated by simulating the completion of the current leg many times and tracking the average payout
   - Players can collect multiple betting tickets, even for the same camel

3. **Race Winner/Loser Bets** and **Terrain Tile Placement** will be implemented in future versions.

## Strategic Insights

Based on our analysis, optimal play in Camel Up often involves:

1. **Ticket Position Consideration**: Taking early betting tickets (1st and 2nd tickets) for camels with high winning probabilities to maximize potential payouts
2. **Opportunity Assessment**: Recognizing when it's better to take the pyramid ticket (guaranteed 1 coin) over any betting ticket
3. **Probability-Based Decisions**: Using the calculated probabilities to make informed bets

The ticket scarcity mechanism (only 4 tickets per camel) and the position-based payouts create an interesting strategic element. Players must decide not only which camel to bet on but also whether to take early tickets with higher payouts for less likely winners, or later tickets with lower payouts for more likely winners.

## Interpreting Results

The `analyze_ev.py` script provides:

1. Expected values for each possible action
2. Comparison between random and optimal strategies
3. A "skill factor" measurement showing the percentage improvement optimal play offers over random play

A large skill factor indicates the game rewards skillful play, while a small factor suggests the game is more chance-based.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.