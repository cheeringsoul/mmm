from asyncio import Queue

from mmm.core.hub.base import MessageHub


class AsyncioQueueEventHub(MessageHub):

    def __init__(self):
        super().__init__()
        self._subscriptions = {}

    def subscribe(self, event_type):
        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = Queue()
        return self._subscriptions[event_type]

    def unsubscribe(self, event_type):
        if event_type in self._subscriptions:
            del self._subscriptions[event_type]

    def publish(self, msg):
        if type(msg) in self._subscriptions:
            self._subscriptions[type(msg)].put_nowait(msg)


class RabbitmqEventHub(MessageHub):

    def publish(self, msg):
        pass

    def subscribe(self, *args, **kwargs):
        pass

    def unsubscribe(self, *args, **kwargs):
        pass


