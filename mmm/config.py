import importlib
import os

from mmm.exceptions import ImproperlyConfigured

empty = object()


class Settings:
    def __init__(self, settings_module):
        mod = importlib.import_module(settings_module)
        for setting in dir(mod):
            if setting.isupper():
                value = getattr(mod, setting)
                setattr(self, setting, value)


class LazySettings:
    """
    setting example:

    DATABASE = {
        'type': 'sqlite'
        'db_path': '/tmp/mmm.db'
    }

    """
    def __init__(self):
        self._wrapped = empty

    def _set_up(self):
        settings_module = os.environ.get('MMM_CONFIG_MODULE')
        if not settings_module:
            raise ImproperlyConfigured('settings are not configured.')
        self._wrapped = Settings(settings_module)

    def __getattr__(self, name):
        if self._wrapped is empty:
            self._set_up()
        try:
            return getattr(self._wrapped, name)
        except AttributeError:
            raise ImproperlyConfigured(f'{name} is not configured.')


settings = LazySettings()
