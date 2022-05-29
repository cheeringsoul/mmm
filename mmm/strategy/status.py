from enum import Enum


class StrategyStatus(Enum):
    OPENED = 1  # 已开仓
    EMPTY = 2  # 空仓
