import asyncio
import json
import logging

import websockets
from abc import ABC, abstractmethod
from mmm.credential import Credential
from mmm.events.event import OrderEvent
from mmm.exceptions import CreateOrderError
from mmm.project_types import OrderResult, OrderStatus
from mmm.third_party.okex.client import Client as OkexClient
from mmm.third_party.okex.trade_api import TradeAPI as OkexTradeAPI


logger = logging.getLogger(__name__)


class OrderHandler(ABC):
    def __init__(self, credential: "Credential"):
        self.credential = credential

    @abstractmethod
    async def create_order(self, order_event: "OrderEvent"):
        pass

    @abstractmethod
    def query_order(self, *args, **kwargs):
        pass


class OkexOrderHandler(OrderHandler):

    def __init__(self, credential: "Credential"):
        self.ws_uri = 'wss://ws.okx.com:8443/ws/v5/private'
        super().__init__(credential)
        self.client = OkexClient(credential.api_key, credential.secret_key, credential.phrase)
        self.trade_client = OkexTradeAPI(credential.api_key, credential.secret_key, credential.phrase)

    async def create_order(self, order_event: "OrderEvent", timeout=8) -> "OrderResult":
        client_order_id = order_event.params['clOrdId']
        inst_id = order_event.params['instId']
        result = OrderResult(
            uniq_id=order_event.uniq_id,
            exchange=order_event.exchange,
            strategy_name=order_event.strategy_name,
            strategy_bot_id=order_event.strategy_bot_id,
            client_order_id=client_order_id,
            order_params=order_event.params,
            status=OrderStatus.CREATED
        )
        try:
            async with websockets.connect(self.ws_uri) as websocket:
                params = json.dumps(order_event.params)
                await websocket.send(params)
                rv = await websocket.recv()
                resp = json.loads(rv)
                if resp['code'] != '0':
                    result.status = OrderStatus.FAILED
                    result.msg = f"create order error, params: {params}, error code: {resp['code']}," \
                                 f" error msg: {resp['msg']}"
                else:
                    rv = await self.query_order(inst_id, client_order_id)
                    if rv.get('code') != '0':
                        result.status = OrderStatus.FAILED
                        result.msg = f"create order error, params: {params}, error code: {resp['code']}," \
                                     f" error msg: {resp['msg']}"
                    else:
                        order_id = resp['data'][0]['orderId']
                        result.order_id = order_id
                        result.status = OrderStatus.SUCCESS
                        result.raw_data = resp['data']
        except (asyncio.TimeoutError, Exception) as e:
            err = f"create order error, params: {params}, exception: {e}"
            logger.error(err)
            result.status = OrderStatus.FAILED
            result.msg = err
        finally:
            return result

    async def create_batch_order(self):
        ...

    async def query_order(self, inst_id, client_order_id, timeout):
        loop = asyncio.get_running_loop()
        future = loop.run_in_executor(None, self.trade_client.get_orders, client_order_id)
        return await asyncio.wait_for(future, timeout=timeout, loop=loop)


class BinanceOrderHandler(OrderHandler):

    def __init__(self, credential: "Credential"):
        super().__init__(credential)

    async def create_order(self, *args, **kwargs):
        pass

    def query_order(self, client_order_id, timeout):
        pass
