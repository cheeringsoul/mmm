import asyncio
import json
import logging
from typing import List, Optional

from mmm.config import settings
from mmm.core.hub.inner_event_hub.event import BotControlEvent, Command
from mmm.core.strategy.bot import BotRegistry, Bot, BotControlEventHandler
from mmm.core.strategy.strategy import Strategy

logger = logging.getLogger(__name__)


class ControllerServer:
    def __init__(self, control_event_queue):
        self.host = settings.STRATEGY_SERVER['HOST']
        self.port = settings.STRATEGY_SERVER['PORT']
        self.control_event_queue = control_event_queue

    async def run(self):
        server = await asyncio.start_server(self.handler, self.host, self.port)
        async with server:
            await server.serve_forever()

    async def handler(self, reader, writer):
        rv = await reader.read(1000)
        try:
            data = json.loads(rv)
            command, bot_id = data.get('command'), data.get('bot_id')
            event = BotControlEvent(Command(command), bot_id)
            self.control_event_queue.put_nowait(event)
        except Exception as e:
            logger.exception(e)


class StrategyRunner:
    def __init__(self, strategies: List["Strategy"]):
        self.control_event_queue = asyncio.Queue()
        self.server = ControllerServer(self.control_event_queue)
        bot_registry = BotRegistry([Bot(each) for each in strategies])
        self.bot_control_event_handler = BotControlEventHandler(bot_registry)

    async def control_bot(self):
        try:
            while True:
                event: "BotControlEvent" = await self.control_event_queue.get()
                await self.bot_control_event_handler.handel(event)
        except Exception as e:
            logger.exception(e)

    async def listening_event(self):
        server_task = asyncio.create_task(self.server.run(), name='task.strategy_runner.listening_command')
        control_bot_task = asyncio.create_task(self.control_bot(), name='task.strategy_runner.control_bot')
        await asyncio.gather(server_task, control_bot_task)

    async def run(self, bot_id: Optional[str] = None):
        if bot_id:
            self.control_event_queue.put_nowait(BotControlEvent(Command.START_ALL, bot_id))
        else:
            self.control_event_queue.put_nowait(BotControlEvent(Command.START_ALL))
        await self.listening_event()

