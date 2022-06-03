import logging
from typing import List

from mmm.position.utils import get_price
from mmm.project_types import Asset


class StrategyPosition:

    def __init__(self, assets: List[Asset]):
        self._assets = assets
        self._init_worth = self.get_worth()

    def get_current_profit(self):
        return self.get_worth()-self._init_worth

    def get_worth(self, unit='USDT'):
        worth = 0
        for each in self._assets:
            worth += get_price(each.inst_id, unit) * each.amount
        return worth

    def add(self, asset: Asset):
        for each in self._assets:
            if each.inst_id == asset.inst_id:
                each.amount += asset.amount
                break
        else:
            self._assets.append(asset)

    def cost(self, asset: Asset):
        for each in self._assets:
            if each.inst_id == asset.inst_id:
                each.amount -= asset.amount
                break
        else:
            logging.error(f"{asset.inst_id} not available.")

    def get_asset(self, inst_id: str) -> Asset or None:
        for each in self._assets:
            if each.inst_id == inst_id:
                return each
        return None
