# -*- coding: utf-8 -*-

import importlib
import pkgutil
from os import path as pathlib

import click


@click.group()
def xd():
    """a list of handy commands which makes life easier
    """
    pass


current_path = pathlib.dirname(pathlib.abspath(__file__))
for _, name, _ in pkgutil.iter_modules([current_path]):
    if name in ('__init__', '__main__'):
        continue

    module = importlib.import_module('.'+name, 'xd')
    cmd = getattr(module, 'command', None)
    if cmd and isinstance(cmd, click.Command):
        xd.add_command(cmd)


if __name__ == '__main__':
    xd()
