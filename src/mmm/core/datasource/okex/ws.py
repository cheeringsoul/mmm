import json
import logging
import asyncio
import websockets

from typing import Optional, List

from mmm.core.datasource.okex.subscription import OKEXSubscription
from mmm.credential import Credential
from mmm.exceptions import CollectionError
from mmm.third_party.okex.utils import get_local_timestamp, login_params
from mmm.core.datasource.base import DataSource
from mmm.core.datasource.okex.parser import parser_factory
from mmm.core.datasource.parser import ParserFactory


logger = logging.getLogger(__name__)


class OkexWsDatasource(DataSource):
    __uri__ = "wss://wsaws.okex.com:8443/ws/v5/public"  # noqa
    __ping_interval__ = 20

    def __init__(self, credential: Optional["Credential"] = None,
                 factory: "ParserFactory" = parser_factory):
        super().__init__()
        self.received_pong = False
        self.credential: Optional["Credential"] = credential
        self.parser_factory: "ParserFactory" = factory

    async def ping(self, ws):
        await asyncio.sleep(self.__ping_interval__)
        logger.info('send a ping')
        await ws.send("ping")
        self.received_pong = False
        await asyncio.sleep(self.__ping_interval__)
        if not self.received_pong:
            raise CollectionError('looking forward a pong message, but not received.')

    async def subscribe(self, subscriptions: List["OKEXSubscription"]):
        topics = {
            'op': 'subscribe',
            'args': []
        }
        for sub in subscriptions:
            topic = sub.get_topic()
            topics['args'].extend(topic['args'])
        try:
            await self._do_subscribe(json.dumps(topics))
        except CollectionError as e:
            logger.exception("looking forward a pong message, but not received.", exc_info=e)
        except Exception as e:
            logger.exception(e)
            logger.info('reconnecting...')

    async def _do_subscribe(self, topic: str):
        async with websockets.connect(self.__uri__, ping_interval=None) as ws:
            if self.credential is not None:
                timestamp = str(get_local_timestamp())
                login_str = login_params(timestamp,
                                         self.credential.api_key,
                                         self.credential.phrase,
                                         self.credential.secret_key)
                await ws.send(login_str)
                rv = json.loads(await ws.recv())
                if rv['code'] != '0':
                    logger.error(f'login error: {rv}')
                    return
            await ws.send(topic)
            rv = await ws.recv()
            data = json.loads(rv)
            assert data['event'] == 'subscribe', data
            ping = asyncio.create_task(self.ping(ws))
            while True:
                try:
                    data = await ws.recv()
                    if data == 'pong':
                        logger.info('received a pong message')
                        self.received_pong = True
                    else:
                        data = json.loads(data)
                        if data.get('event') == 'subscribe':
                            logger.info(f'subscribe {topic} successfully')
                        elif data.get('event') == 'error':
                            logger.error(f'subscribe {topic} failed, {data}')
                        else:
                            channel = data['arg']['channel']
                            msg = self.parser_factory.get(channel).parse(data)
                            for each in msg:
                                self.ds_msg_hub.publish(each)
                    ping.cancel()
                    ping = asyncio.create_task(self.ping(ws))
                except Exception as e:
                    logger.exception(e)
                    break
