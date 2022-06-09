from abc import ABC, abstractmethod
from mmm.credential import Credential
from mmm.project_types import Order
from mmm.third_party.okex.client import Client as OkexClient


class OrderHandler(ABC):
    def __init__(self, credential: "Credential"):
        self.credential = credential

    @abstractmethod
    def create_order(self, *args, **kwargs):
        pass

    @abstractmethod
    def query_order(self, client_order_id, timeout):
        pass


class OkexOrderHandler(OrderHandler):

    def __init__(self, credential: Credential):
        super().__init__(credential)
        self.client = OkexClient(credential.api_key, credential.secret_key, credential.phrase)

    def create_order(self, **kwargs):
        # todo send order to exchange
        """
        async def hello():
            async with websockets.connect('ws://localhost:8765') as websocket:
                name = input("What's your name? ")

                await websocket.send(name)
                print(f"> {name}")

                greeting = await websocket.recv()
                print(f"< {greeting}")
        asyncio.get_event_loop().run_until_complete(hello())

        """
        client_order_id = kwargs['clOrdId']
        return client_order_id

    def query_order(self, client_order_id, timeout) -> Order:
        # todo query order
        return client_order_id


class BinanceOrderHandler(OrderHandler):

    def __init__(self, credential: Credential):
        super().__init__(credential)

    def create_order(self, *args, **kwargs):
        pass

    def query_order(self, client_order_id, timeout):
        pass
