import asyncio
import click


@click.group()
def cli(): ...


@click.command()
def start_order_executor():
    from mmm.core.order.executor import OrderExecutor

    OrderExecutor().create_task()
    asyncio.get_event_loop().run_forever()


@click.command()
@click.option('--names', '-n', required=True, type=click.Choice(['okex', 'binance']), multiple=True)
@click.option('--topic', '-t', required=True, type=str)
def start_data_source(name, topic):
    from mmm.core.datasource import OkexWsDatasource

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


@click.command()
def init_database():
    from sqlalchemy_utils import database_exists, create_database
    from mmm.core.schema.models import engine, Base

    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(bind=engine)
    click.echo('done.')


cli.add_command(start_order_executor)
cli.add_command(start_data_source)
cli.add_command(start_strategy)
cli.add_command(start_admin)
cli.add_command(init_database)
