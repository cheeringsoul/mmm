import logging

from asyncio import Queue
from typing import Dict

from mmm.core.hub.base import MessageHub
from mmm.core.hub.datasource_msg_hub.subscription import Subscription, ResponseOfSub


logger = logging.getLogger(__name__)


class AsyncioQueueDsMsgHub(MessageHub):
    """asyncio queue datasource message hub."""
    def __init__(self):
        super().__init__()
        self._subscriptions: Dict["Subscription", "Queue"] = {}

    def publish(self, msg: "ResponseOfSub"):
        for subscription, queue in self._subscriptions.items():
            if msg.response_for(subscription):
                queue.put_nowait(msg)

    def subscribe(self, subscription: "Subscription"):
        if subscription not in self._subscriptions:
            self._subscriptions[subscription] = Queue()
        return self._subscriptions[subscription]

    def unsubscribe(self, subscription: "Subscription"):
        if subscription in self._subscriptions:
            del self._subscriptions[subscription]


class RabbitMQDsMsgHub(MessageHub):
    """rabbitmq datasource message hub."""
    def publish(self, msg):
        """todo"""

    def subscribe(self, subscription: "Subscription"):
        """todo"""

    def unsubscribe(self, subscription: "Subscription"):
        """todo"""
