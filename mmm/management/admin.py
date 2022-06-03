import click
from pathlib import Path
import shutil


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


admin_cli.add_command(create_project)
