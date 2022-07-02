from abc import ABCMeta, abstractmethod


class MessageHub(metaclass=ABCMeta):

    @abstractmethod
    def publish(self, msg): ...

    @abstractmethod
    def subscribe(self, *args, **kwargs): ...

    @abstractmethod
    def unsubscribe(self, *args, **kwargs): ...
