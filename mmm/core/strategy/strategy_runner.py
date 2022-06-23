import asyncio
import logging
from typing import List, Optional

from mmm.config import settings
from mmm.core.events.event import BotControlEvent, Command
from mmm.core.strategy.bot import BotRegistry, Bot
from mmm.core.strategy.strategy import Strategy

logger = logging.getLogger(__name__)


class ControllerServer:
    def __init__(self):
        self.event_source = settings.EVENT_SOURCE_CONF[BotControlEvent]
        self.host = settings.STRATEGY_SERVER['HOST']
        self.port = settings.STRATEGY_SERVER['PORT']

    async def run(self):
        server = await asyncio.start_server(self.handler, self.host, self.port)
        async with server:
            await server.serve_forever()

    async def handler(self, reader, writer):
        ...


class StrategyRunner:
    def __init__(self, strategies: List["Strategy"]):
        self.server = ControllerServer()
        self.event_source = settings.EVENT_SOURCE_CONF[BotControlEvent]
        self.bot_registry = BotRegistry([Bot(each) for each in strategies])
        self.tasks = {}

    async def monitor(self):
        try:
            while True:
                event: "BotControlEvent" = await self.event_source.get()
                await self.control_bot(event)

        except Exception as e:
            logger.exception(e)

    async def run(self):
        server_task = asyncio.create_task(self.server.run(), name='task.controller_server')
        monitor_task = asyncio.create_task(self.monitor(), name='task.strategy_runner.monitor')
        await asyncio.gather(server_task, monitor_task)

    async def start(self, bot_id: Optional[str] = None):
        if bot_id:
            self.event_source.put_nowait(BotControlEvent(Command.START_ALL, bot_id))
        else:
            self.event_source.put_nowait(BotControlEvent(Command.START_ALL))
        await self.run()

    async def control_bot(self, event: "BotControlEvent"):
        if event.command == Command.START_ALL:
            bots = self.bot_registry.get_all_bot()
            for bot in bots:
                if bot.bot_id not in self.tasks:
                    self.tasks[bot.bot_id] = asyncio.create_task(bot.gather_tasks())
        elif event.command == Command.START_BOT:
            bot_id = event.bot_id
            if bot_id not in self.tasks:
                bot = self.bot_registry.get_bot(bot_id)
                self.tasks[bot_id] = asyncio.create_task(bot.gather_tasks())
        elif event.command == Command.STOP_BOT:
            bot_id = event.bot_id
            task = self.tasks.get(bot_id)
            if task:
                task.cancel()
                del self.tasks[bot_id]
        elif event.command == Command.STOP_ALL:
            for _, task in self.tasks.items():
                task.cancel()
            self.tasks = {}
