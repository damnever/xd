# -*- coding: utf-8 -*-

import sys
import shlex

import click

from .batch import Batch


__version__ = '0.1.3'
version_info = [int(num) for num in __version__.split('.')]


@click.group()
def xd():
    """a list of handy commands which makes life easier
    """
    pass


@click.command()
def version():
    "show version"
    click.echo('xd v' + __version__)


@click.command()
@click.argument('cmd', nargs=-1)
@click.option('-c', '--count', type=int, default=2, show_default=True,
              help='The max tasks in parallel.')
@click.option('-s', '--step', type=int, default=1, show_default=True,
              help='Execute by step, each time (count/step) task in parallel.')
@click.option('-i', '--interval', type=float, default=1, show_default=True,
              help=('Sleep interval seconds between each step,'
                    ' ignored if step is 1.'))
@click.option('-e', '--err-exit', is_flag=True, default=True,
              show_default=True,
              help='Exit all if one of the tasks exit abnormally.')
def batch(cmd, count, step, interval, err_exit):
    """
    execute a program multiple times in parallel

        xd batch echo hello world

        xd batch -c 5 "sh -c 'echo hello; sleep 1; echo world'"

        xd batch -c 7 -- sh -c 'echo hello; sleep 1; echo world'
    """
    if count < 1:
        click.secho('count must greater than 0', fg='red')
        sys.exit(1)
    if len(cmd) == 0:
        click.secho('[CMD]... is required, see usage for details', fg='red')
        sys.exit(1)
    if len(cmd) == 1:
        cmd = shlex.split(cmd[0])
    Batch(list(cmd), count, step, interval, err_exit)()


@click.command()
def watch():
    """execute a program periodically"""
    click.echo('not available, google watch command instead..')


xd.add_command(version)
xd.add_command(batch)
xd.add_command(watch)


if __name__ == '__main__':
    xd()
