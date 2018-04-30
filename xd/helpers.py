# -*- coding: utf-8 -*-

import os
import sys
from contextlib import contextmanager

import click


class ClickListOption(click.Option):
    def type_cast_value(self, ctx, value):
        if not value:
            return []
        return value.split(',')


def abort(fmt, *args):
    msg = ' ' + fmt.format(*args)
    click.secho(msg, fg='red')
    sys.exit(1)


@contextmanager
def err_abort(fmt, *args):
    try:
        yield
    except Exception as e:
        msg = fmt.format(*args)
        abort('{}: {}', msg, e)


@contextmanager
def cd(path):
    cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(cwd)
