# -*- coding: utf-8 -*-

import click


version = __version__ = '0.1.8'
version_info = [int(num) for num in __version__.split('.')]


@click.command(name='version')
def command():
    "Show version."
    click.echo('xd v' + version)
