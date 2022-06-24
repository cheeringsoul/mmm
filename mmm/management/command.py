import asyncio
import json

import click
from prettytable import PrettyTable

from mmm.config import settings
from sqlalchemy_utils import database_exists, create_database


@click.group()
def cli(): ...


@click.command()
def start_order_executor():
    from mmm.core.order.executor import OrderExecutor

    OrderExecutor().create_task()
    asyncio.get_event_loop().run_forever()


@click.command()
@click.option('--name', '-n', required=True, type=click.Choice(['okex', 'binance']))
@click.option('--topic', '-t', required=True, type=str)
def start_data_source(name, topic):
    from mmm.core.datasource import OkexWsDatasource

    if name == 'okex':
        task = OkexWsDatasource().subscribe(topic)
    elif name == 'binance':
        """todo"""
    asyncio.run(task)


@click.command()
@click.option('--bot-id', default=None, help='bot id of strategy. if None, it will start all bots.')
@click.option('--with-datasource', type=click.Choice(['okex', 'binance']),
              help='If you start a strategy bot with all-alone model, you must specify a datasource. '
                   'If you start strategy bot with distributed model, then you can ignore this option')
@click.option('--topic', type=str, help="If you use all-alone model, you must specify topic to subscribe.")
def start_strategy(bot_id, with_datasource=None, topic=None):
    from mmm.config.tools import load_strategy_app
    from mmm.core.strategy import StrategyRunner
    from mmm.core.datasource import OkexWsDatasource

    apps = load_strategy_app(settings.STRATEGIES)
    if with_datasource == 'okex' and topic:
        async def main():
            task1 = OkexWsDatasource().subscribe(topic)
            task2 = StrategyRunner(apps).start_strategy(bot_id)
            await asyncio.gather(task1, task2)
        asyncio.run(main())
    elif with_datasource == 'binance' and topic:
        ...
    else:
        asyncio.run(StrategyRunner(apps).start_strategy(bot_id))


@click.command()
@click.option('--with-datasource', type=click.Choice(['okex', 'binance']),
              help='If you start a strategy bot with all-alone model, you must specify a datasource. '
                   'If you start strategy bot with distributed model, then you can ignore this option')
@click.option('--topic', type=str, help="If you use all-alone model, you must specify topic to subscribe.")
def prepare_strategy(with_datasource=None, topic=None):
    from mmm.config.tools import load_strategy_app
    from mmm.core.strategy import StrategyRunner
    from mmm.core.datasource import OkexWsDatasource

    apps = load_strategy_app(settings.STRATEGIES)
    click.echo(f"listening control command...")
    if with_datasource == 'okex' and topic:
        async def main():
            task1 = OkexWsDatasource().subscribe(topic)
            task2 = StrategyRunner(apps).start()
            await asyncio.gather(task1, task2)
        asyncio.run(main())
    elif with_datasource == 'binance' and topic:
        ...
    else:
        asyncio.run(StrategyRunner(apps).start())


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
