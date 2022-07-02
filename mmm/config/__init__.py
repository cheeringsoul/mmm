import importlib
import os
from frozendict import frozendict

from mmm.exceptions import ConfigureError

empty = object()


class Settings:
    def __init__(self, settings_module):
        default_config = 'mmm.config.default_config'
        self._set_config(default_config)
        self._set_config(settings_module)

    def __setattr__(self, key, value):
        setattr(self, key, value)

    def _set_config(self, settings_module):
        mod = importlib.import_module(settings_module)
        for setting in dir(mod):
            if setting.isupper():
                value = getattr(mod, setting)
                if setting == 'STRATEGIES':
                    if not all([':' in each for each in value]):
                        raise ConfigureError('STRATEGIES configured incorrectly.')
                setattr(self, setting, value)


class LazySettings:
    def __init__(self):
        self._wrapped = empty

    def _set_up(self):
        settings_module = os.environ.get('MMM_SETTINGS_MODULE')
        if not settings_module:
            raise ConfigureError('setting module is not configured.')
        self._wrapped = Settings(settings_module)

    def __setattr__(self, key, value):
        setattr(self._wrapped, key, value)

    def __getattr__(self, name):
        if self._wrapped is empty:
            self._set_up()
        try:
            return getattr(self._wrapped, name)
        except AttributeError:
            raise ConfigureError(f'{name} is not configured.')


settings = LazySettings()
