import importlib
from typing import List


def load_strategy_app(strategy: List[str]):
    apps = []
    for each in strategy:
        mod_str, app_str = each.split(':')
        mod = importlib.import_module(mod_str)
        app = getattr(mod, app_str)
        apps.append(app)
    return apps
