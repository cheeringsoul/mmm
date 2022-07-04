from mmm.config import settings
from mmm.core.hub.datasource_msg_hub.hub import AsyncioQueueDsMsgHub, RabbitMQDsMsgHub
from mmm.core.hub.inner_event_hub.hub import AsyncioQueueEventHub, RabbitmqEventHub
from mmm.project_types import RunningModel


def singleton(cls):
    _instance = {}

    def _singleton(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return _singleton


@singleton
class HubFactory:
    def __init__(self):
        self._ds_msg_hub = None
        self._inner_event_hub = None

    def get_ds_msg_hub(self):
        """get datasource message hub"""

        if settings.MODEL == RunningModel.ALL_ALONE:
            if self._ds_msg_hub is None:
                self._ds_msg_hub = AsyncioQueueDsMsgHub()
            return self._ds_msg_hub
        elif settings.MODEL == RunningModel.DISTRIBUTED:
            return RabbitMQDsMsgHub()

    def get_inner_event_hub(self):
        if settings.MODEL == RunningModel.ALL_ALONE:
            if self._inner_event_hub is None:
                self._inner_event_hub = AsyncioQueueEventHub()
            return self._inner_event_hub
        elif settings.MODEL == RunningModel.DISTRIBUTED:
            return RabbitmqEventHub()
