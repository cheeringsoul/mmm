import json
import logging
import asyncio
import websockets

from .parser import ParserFactory, parser_factory
from mmm.core.events.event import Event
from mmm.core.events.dispatcher import Dispatcher


logger = logging.getLogger(__name__)


class CollectionError(Exception):
    """"""


class OkexWsDatasource:
    __uri__ = "wss://wsaws.okex.com:8443/ws/v5/public"  # noqa
    __ping_interval__ = 20

    def __init__(self, factory: "ParserFactory" = parser_factory):
        self.received_pong = False
        self.parser_factory: "ParserFactory" = factory
        self.dispatcher = Dispatcher()

    async def ping(self, ws):
        await asyncio.sleep(self.__ping_interval__)
        logger.info('send a ping')
        await ws.send("ping")
        self.received_pong = False
        await asyncio.sleep(self.__ping_interval__)
        if not self.received_pong:
            raise CollectionError('looking forward a pong message, but not received.')

    def subscribe(self, topic: str):
        async def create_task():
            while True:
                try:
                    await self._do_subscribe(topic)
                except CollectionError as e:
                    logger.exception("looking forward a pong message, but not received.", exc_info=e)
                except Exception as e:
                    logger.exception(e)
                    logger.info('reconnecting...')
        loop = asyncio.get_event_loop()
        loop.create_task(create_task(), name=f'task.okex.ws.sub.{topic}')

    async def _do_subscribe(self, topic: str):
        async with websockets.connect(self.__uri__, ping_interval=None) as ws:
            await ws.send(topic)
            msg = await ws.recv()
            msg = json.loads(msg)
            assert msg['event'] == 'subscribe', msg
            ping = asyncio.create_task(self.ping(ws))
            while True:
                try:
                    msg = await ws.recv()
                    if msg == 'pong':
                        logger.info('received a pong message')
                        self.received_pong = True
                    else:
                        msg = json.loads(msg)
                        if msg.get('event') == 'subscribe':
                            logger.info(f'subscribe {topic} successfully')
                        elif msg.get('event') == 'error':
                            logger.error(f'subscribe {topic} failed, {msg}')
                        else:
                            channel = msg['arg']['channel']
                            event = self.parser_factory.get(channel).parse(msg)
                            if isinstance(event, Event):
                                await self.dispatcher.dispatch(event)
                            elif isinstance(event, list):
                                for each in event:
                                    await self.dispatcher.dispatch(each)
                    ping.cancel()
                    ping = asyncio.create_task(self.ping(ws))
                except Exception as e:
                    logger.exception(e)
                    break
