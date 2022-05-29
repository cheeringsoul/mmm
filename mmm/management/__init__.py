import sys
from mmm.management import commands


def execute_from_command_line():
    command = sys.argv[1]
    params = sys.argv[2:]
    try:
        executable = getattr(commands, command)
        executable(*params)
    except AttributeError:
        raise RuntimeError(f'command {command} not found')
