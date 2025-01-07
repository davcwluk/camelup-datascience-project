# camelup/__init__.py

from .game import CamelUpGame
from .models import Camel
from .board import Board
from .dice import Dice
from .probability_calculator import ProbabilityCalculator
# from .betting import BettingSystem

__all__ = ['CamelUpGame', 'Camel', 'Board', 'Dice']  # Add 'BettingSystem' if applicable
