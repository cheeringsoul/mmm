from mmm.project_types import RunningModel

STRATEGIES = []

DATABASE = 'sqlite:///mmm.db'
MODEL = RunningModel.ALL_ALONE
STRATEGY_SERVER = {  # strategy server that receive control message
    'HOST': '0.0.0.0',
    'PORT': 6666,
}
