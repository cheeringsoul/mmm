import asyncio
import click

from mmm.datasource import OkexWsDatasource
from mmm.order.executor import OrderExecutor


@click.group()
def cli(): ...


@click.command()
def start_order_executor():
    OrderExecutor().create_task()
    asyncio.get_event_loop().run_forever()


@click.command()
@click.option('--names', '-n', required=True, type=click.Choice(['okex', 'binance']), multiple=True)
@click.option('--topic', '-t', required=True, type=str)
def start_data_source(name, topic):
    if name == 'okex':
        OkexWsDatasource().subscribe(topic)
    elif name == 'binance':
        """todo"""
    asyncio.get_event_loop().run_forever()


@click.command()
@click.option('--name', '-n', required=True)
def start_strategy(name):
    """todo"""


@click.command()
@click.option('--host', '-h', default='127.0.0.1')
@click.option('--port', '-p', default='8888')
def start_admin(host, port):
    """todo"""


cli.add_command(start_order_executor)
cli.add_command(start_data_source)
cli.add_command(start_strategy)
cli.add_command(start_admin)
