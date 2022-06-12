import click
import shutil

from jinja2 import Template
from pathlib import Path


@click.group()
def admin_cli(): ...


@click.command()
@click.option('--name', '-n', help='name of the project.', required=True, type=str)
@click.option('--path', '-p', help='path of the project, default current path', type=str)
def create_project(name, path=None):
    if path is None:
        path = Path.cwd()
    else:
        path = Path(path)
    dst = path/Path(name)
    if dst.exists():
        click.echo(f"{dst} exists.")
        return
    src = Path(__file__).parent.parent.resolve()/Path('template')
    shutil.copytree(src, dst)
    tpl = """
import os
from mmm.management.command import cli


if __name__ == '__main__':
    os.environ.get('MMM_SETTINGS_MODULE', 'settings')
    cli()

"""
    rv = Template(tpl).render({'name_upper': name.upper(), 'name': name})
    manager = Path(dst/Path('manager.py'))
    with open(manager, 'w') as f:
        f.write(rv)


admin_cli.add_command(create_project)
