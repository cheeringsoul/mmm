from decimal import Decimal

import yaml

from typing import List
from mmm.project_types import Asset


class StrategyConfig:
    def __init__(self, assets: List[Asset], max_loss: Decimal):
        self.init_assets = assets
        self.max_loss = max_loss

    @classmethod
    def load_from_path(cls, path: str):
        with open(path) as f:
            rv = yaml.safe_load(f)
            assets = []
            for k, v in rv['init_assets']:
                assets.append(Asset(k, v))
            max_loss = rv['max_loss']
            return cls(assets, max_loss)
