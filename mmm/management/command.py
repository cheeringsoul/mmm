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
    asyncio.run(_start_data_source())


async def _start_data_source():
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
            tasks.append(OkexWsDatasource().subscribe(subs))
        elif exchange == Exchange.BINANCE:
            tasks.append(BinanceWsDatasource().subscribe(subs))
    return tasks


@click.command()
@click.option('--bot-id', default=None, help='bot id of strategy. if None, it will start all bots.')
@click.option('--running-model', default='all_alone')
def start_strategy(bot_id):
    from mmm.core.order.executor import OrderExecutor
    from mmm.core.strategy import StrategyRunner

    settings.MODEL = RunningModel.ALL_ALONE
    apps = load_strategy_app(settings.STRATEGIES)

    async def main():
        tasks = []
        datasource_tasks = _start_data_source()
        strategy_task = StrategyRunner(apps).run(bot_id)
        order_executor_task = OrderExecutor().run_executor()
        tasks.append(datasource_tasks)
        tasks.append(strategy_task)
        tasks.append(order_executor_task)
        await asyncio.gather(*tasks)

    asyncio.run(main())


@click.command()
def prepare_strategy(with_datasource=None, topic=None):
    from mmm.config.tools import load_strategy_app
    from mmm.core.strategy import StrategyRunner
    from mmm.core.datasource import OkexWsDatasource

    apps = load_strategy_app(settings.STRATEGIES)
    click.echo(f"listening control command...")
    if with_datasource == 'okex' and topic:
        async def main():
            task1 = OkexWsDatasource().subscribe(topic)
            task2 = StrategyRunner(apps).listening_event()
            await asyncio.gather(task1, task2)
        asyncio.run(main())
    elif with_datasource == 'binance' and topic:
        ...
    else:
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
cli.add_command(prepare_strategy)
cli.add_command(start_strategy)
cli.add_command(list_strategy)
cli.add_command(start_dashboard)
cli.add_command(init_database)
