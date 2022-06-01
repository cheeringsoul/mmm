import logging
from typing import List

from mmm.position.utils import get_price
from mmm.project_types import Asset


class StrategyPosition:
    """仓位管理器"""

    def __init__(self, assets: List[Asset]):
        self._assets = assets
        self._init_worth = self.get_worth()

    def get_profit(self):
        """当前利润"""
        return self.get_worth()-self._init_worth

    def get_worth(self):
        """获取资产价值, USDT计价"""
        worth = 0
        for each in self._assets:
            worth += get_price(each.inst_id, 'USDT') * each.amount
        return worth

    def add(self, asset: Asset):
        """添加资产"""
        for each in self._assets:
            if each.inst_id == asset.inst_id:
                each.amount += asset.amount
                break
        else:
            self._assets.append(asset)

    def cost(self, asset: Asset):
        """花费资产"""
        for each in self._assets:
            if each.inst_id == asset.inst_id:
                each.amount -= asset.amount
                break
        else:
            logging.error(f"仓位中没有{asset.inst_id}资产")

    def get_asset(self, inst_id: str) -> Asset or None:
        """获取资产"""
        for each in self._assets:
            if each.inst_id == inst_id:
                return each
        return None
