import asyncio
import click
from collections import defaultdict
from prettytable import PrettyTable
from sqlalchemy_utils import database_exists, create_database

from mmm.config import settings
from mmm.config.tools import load_strategy_app
from mmm.project_types import Exchange, RunningModel


@click.group()
def cli(): ...


@click.command()
def start_order_executor():
    from mmm.core.order.executor import OrderExecutor

    settings.MODEL = RunningModel.DISTRIBUTED
    asyncio.run(OrderExecutor().run_executor())


@click.command()
def start_data_source():
    settings.MODEL = RunningModel.DISTRIBUTED
    async def main():
        tasks = _start_data_source
        asyncio.gather(*tasks)
    asyncio.run(main())


def _start_data_source():
    from mmm.core.datasource import OkexWsDatasource
    from mmm.core.datasource.binance import BinanceWsDatasource

    apps = load_strategy_app(settings.STRATEGIES)
    exchange_sub_conf = defaultdict(list)
    for app in apps:
        subscriptions = app.get_subscriptions()
        for sub in subscriptions:
            exchange_sub_conf[sub.get_exchange()].append(sub)
    tasks = []
    for exchange, subs in exchange_sub_conf.items():
        if exchange == Exchange.OKEX:
            tasks.append(asyncio.create_task(OkexWsDatasource().subscribe(subs), name='task.okex_datasource'))
        elif exchange == Exchange.BINANCE:
            tasks.append(asyncio.create_task(BinanceWsDatasource().subscribe(subs), name='task.binance_datasource'))
    return tasks


def _prepare_strategy_tasks():
    from mmm.core.order.executor import OrderExecutor

    tasks = []
    datasource_tasks = _start_data_source()
    order_executor_task = asyncio.create_task(OrderExecutor().run_executor(), name='task.order_executor')
    tasks.extend(datasource_tasks)
    tasks.append(order_executor_task)
    return tasks


@click.command()
@click.option('--bot-id', default=None, help='bot id of strategy. if None, it will start all bots.')
@click.option('--running-model', default='all_alone',
              type=click.Choice(['all_alone', 'distributed'], case_sensitive=False))
def start_strategy(bot_id, running_model='all_alone'):
    from mmm.core.strategy import StrategyRunner

    apps = load_strategy_app(settings.STRATEGIES)

    if running_model.upper() == 'ALL_ALONE':
        settings.MODEL = RunningModel.ALL_ALONE

        async def main():
            tasks = _prepare_strategy_tasks()
            strategy_task = asyncio.create_task(StrategyRunner(apps).run(bot_id), name='task.start_strategy')
            tasks.append(strategy_task)
            await asyncio.gather(*tasks)

        asyncio.run(main())
    else:
        settings.MODEL = RunningModel.DISTRIBUTED
        asyncio.run(StrategyRunner(apps).run(bot_id))


@click.command()
@click.option('--running-model', default='all_alone',
              type=click.Choice(['all_alone', 'distributed'], case_sensitive=False))
def strategy_listening(running_model='all_alone'):
    from mmm.config.tools import load_strategy_app
    from mmm.core.strategy import StrategyRunner

    apps = load_strategy_app(settings.STRATEGIES)
    if running_model.upper() == 'ALL_ALONE':
        settings.MODEL = RunningModel.ALL_ALONE

        async def main():
            tasks = _prepare_strategy_tasks()
            strategy_task = asyncio.create_task(StrategyRunner(apps).listening_event(), name='task.strategy_listening')
            tasks.append(strategy_task)
            await asyncio.gather(*tasks)

        asyncio.run(main())
    else:
        settings.MODEL = RunningModel.DISTRIBUTED
        asyncio.run(StrategyRunner(apps).listening_event())


@click.command()
def list_strategy():
    from mmm.config.tools import load_strategy_app

    apps = load_strategy_app(settings.STRATEGIES)
    tbl = PrettyTable()
    tbl.field_names = ["Strategy", "bot id"]
    rows = [[each.strategy_name, each.bot_id] for each in apps]
    tbl.add_rows(rows)
    click.echo(tbl)


@click.command()
@click.option('--host', '-h', default='127.0.0.1')
@click.option('--port', '-p', default='8888')
def start_dashboard(host, port):
    from mmm.dashboard.app import application

    application.run(host=host, port=int(port))


@click.command()
def init_database():
    from mmm.schema import engine
    from mmm.schema.models import Base

    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(bind=engine)
    click.echo('done.')


cli.add_command(start_order_executor)
cli.add_command(start_data_source)
cli.add_command(strategy_listening)
cli.add_command(start_strategy)
cli.add_command(list_strategy)
cli.add_command(start_dashboard)
cli.add_command(init_database)
