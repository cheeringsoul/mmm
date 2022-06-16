import asyncio
import json
import logging
import traceback

import websockets
from abc import ABC, abstractmethod
from mmm.credential import Credential
from mmm.core.events.event import OrderEvent
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
        super().__init__(credential)
        self.trade_client = OkexTradeAPI(credential.api_key, credential.secret_key, credential.phrase,
                                         use_server_time=True, flag='0')

    async def create_order(self, order_event: "OrderEvent", timeout=8) -> "OrderResult":
        params = order_event.params
        client_order_id = params['clOrdId']
        inst_id = params['instId']
        result = OrderResult(
            uniq_id=order_event.uniq_id,
            exchange=order_event.exchange,
            strategy_name=order_event.strategy_name,
            strategy_bot_id=order_event.bot_id,
            client_order_id=client_order_id,
            order_params=params,
            status=OrderStatus.CREATED
        )
        try:
            loop = asyncio.get_running_loop()
            future = loop.run_in_executor(None, self.trade_client.place_order, params)
            resp = await asyncio.wait_for(future, timeout=timeout)
            if resp['code'] != '0':
                result.status = OrderStatus.FAILED
                result.msg = f"create order error, params: {params}, error code: {resp['code']}," \
                             f" error msg: {resp['msg']}"
            else:
                rv = await self.query_order(inst_id, client_order_id, timeout)
                if rv.get('code') != '0':
                    result.status = OrderStatus.FAILED
                    result.msg = f"query order error, params: {params}, response: {rv}"

                else:
                    order_id = resp['data'][0]['orderId']
                    result.order_id = order_id
                    result.status = OrderStatus.SUCCESS
                    result.raw_data = resp
        except (asyncio.TimeoutError, Exception) as e:
            tb = traceback.format_exc()
            err = f"create order error, params: {params}, exception: {e}, traceback: {tb}"
            logger.error(err)
            result.status = OrderStatus.FAILED
            result.msg = err
        finally:
            return result

    async def create_batch_order(self):
        ...

    async def query_order(self, inst_id, client_order_id, timeout):
        loop = asyncio.get_running_loop()
        future = loop.run_in_executor(None, self.trade_client.get_orders, inst_id, client_order_id)
        return await asyncio.wait_for(future, timeout=timeout)


class BinanceOrderHandler(OrderHandler):

    def __init__(self, credential: "Credential"):
        super().__init__(credential)

    async def create_order(self, *args, **kwargs):
        pass

    def query_order(self, client_order_id, timeout):
        pass
