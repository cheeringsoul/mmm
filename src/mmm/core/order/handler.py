import asyncio
import json
import logging
import traceback

from abc import ABC, abstractmethod

from mmm.core.hub.inner_event_hub.event import OrderCreationEvent
from mmm.credential import Credential
from mmm.project_types import OrderResult, OrderStatus
from mmm.third_party.okex.trade_api import TradeAPI as OkexTradeAPI


logger = logging.getLogger(__name__)


class OrderHandler(ABC):
    def __init__(self, credential: "Credential"):
        self.credential = credential

    @abstractmethod
    async def create_order(self, event: "OrderCreationEvent"):
        pass

    @abstractmethod
    def query_order(self, *args, **kwargs):
        pass


class OkexOrderHandler(OrderHandler):

    def __init__(self, credential: "Credential"):
        super().__init__(credential)
        self.trade_client = OkexTradeAPI(credential.api_key, credential.secret_key, credential.phrase,
                                         use_server_time=True, flag='0')

    async def create_order(self, order_event: "OrderCreationEvent") -> "OrderResult":
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
            resp = await asyncio.to_thread(self.trade_client.place_order, params)
            if resp['code'] != '0':
                result.status = OrderStatus.FAILED
                result.msg = json.dumps(resp)
        except Exception as e:
            tb = traceback.format_exc()
            err = f"create order error, params: {params}, exception: {e}, traceback: {tb}"
            logger.error(err)
        finally:
            rv = await self.query_order(inst_id, client_order_id)
            if rv.get('code') != '0':
                result.status = OrderStatus.FAILED
                result.msg = json.dumps(rv)
            else:
                result.exchange_resp = rv
                order_id = rv['data'][0]['ordId']
                result.order_id = order_id
                result.status = OrderStatus.SUCCESS
            return result

    async def create_batch_order(self):
        ...

    async def query_order(self, inst_id, client_order_id):
        return await asyncio.to_thread(self.trade_client.get_orders, inst_id, client_order_id)


class BinanceOrderHandler(OrderHandler):

    def __init__(self, credential: "Credential"):
        super().__init__(credential)

    async def create_order(self, *args, **kwargs):
        pass

    def query_order(self, client_order_id, timeout):
        pass
