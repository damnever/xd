# -*- coding: utf-8 -*-

import click


__version__ = '0.1.4'
version_info = [int(num) for num in __version__.split('.')]


@click.command()
def version():
    "show version"
    click.echo('xd v' + __version__)
