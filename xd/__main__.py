# -*- coding: utf-8 -*-

import click

from .__version__ import version
from .batch import batch
from .watch import watch
from .gitinit import gitinit


@click.group()
def xd():
    """a list of handy commands which makes life easier
    """
    pass


xd.add_command(version)
xd.add_command(batch)
xd.add_command(watch)
xd.add_command(gitinit)


if __name__ == '__main__':
    xd()
