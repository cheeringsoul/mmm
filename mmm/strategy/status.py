from enum import Enum


class StrategyStatus(Enum):
    OPENED = 1  # already opened a position
    SHORT = 2  # short position
