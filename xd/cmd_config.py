# -*- coding: utf-8 -*-

import io
import json
from os import path as pathlib
from functools import partial
from collections import OrderedDict
try:
    from configparser import ConfigParser
except ImportError:
    from backports.configparser import ConfigParser  # Fuck Py2

import click
import yaml
import pytoml as toml
from six import PY2

from .helpers import abort, err_abort


StringIO = io.BytesIO if PY2 else io.StringIO


@click.command(name='config')
@click.option(
    '-t', '--file-type', type=str,
    help='The type of config file, detect it by extension by default.')
@click.option(
    '-q', '--query', type=str,
    help=('Query field(s) by python style operators, use {X} as the object'
          ' placeholder and doubling {{X}} to escape {X}.'))
@click.option(
    '-c', '--convert-into', type=str,
    help='Convert config into a different file type and output the content.')
@click.option(
    '-n', '--no-newline', is_flag=True, default=False, show_default=True,
    help='No newline at the end of output.')
@click.argument('file', nargs=-1, type=click.File(mode='rb'))
def command(file_type, query, convert_into, file, no_newline):
    """
    Manipulate config files: json, yaml, ini and toml.

        cat Pipfile | xd config -t toml -q "{X}['packages']" # query fields

        xd config -c json xxoo.toml                # convert toml into json
    """
    if not file:
        if not file_type:
            abort('can not detect file type without a named file')
        file = click.get_text_stream('stdin')
    else:
        file = file[0]
        if not file_type:
            _, file_type = pathlib.splitext(file.name)

    if query:
        query_config(_load(file_type, file), query, no_newline)
    elif convert_into:
        convert_config(_load(file_type, file), convert_into, no_newline)
    else:
        abort('--query or --convert-into is required')


def query_config(obj, query, no_newline):
    with err_abort('invalid expression or query string'):
        # Using https://github.com/damnever/fmt? ^_^
        ns = {}
        expr = '_xd_query_=' + query.format(X='obj')
        exec(expr, {'obj': obj}, ns)
        res = json.dumps(ns['_xd_query_'], indent=4)  # dump..
        click.echo(res, nl=(not no_newline))


def convert_config(obj, typ, no_newline):
    click.echo(_dumps(typ, obj), nl=(not no_newline))


def _load(typ, file):
    return _parser_do(typ, file, 'load')


def _dumps(typ, obj):
    return _parser_do(typ, obj, 'dumps')


def _parser_do(typ, arg, action):
    parsers = {  # ?
        'json': JSON,
        'yaml': YAML,
        'yml': YAML,
        'ini': INI,
        'toml': toml,
    }
    typ = typ.lstrip('.').lower()
    parser = parsers.get(typ, None)
    if not parser:
        abort('file type {} is not supported', typ)

    assert action in {'load', 'dumps'}, 'fuck me'
    with err_abort('{} config failed', action):
        return getattr(parser, action)(arg)


class JSON(object):
    load = staticmethod(json.load)
    dumps = staticmethod(partial(json.dumps, indent=2))


class YAML(object):
    yaml.Dumper.add_representer(
        OrderedDict,
        lambda dumper, d: dumper.represent_dict(d.items()),
    )

    load = staticmethod(yaml.full_load)
    # XXX: default_flow_style??
    dumps = staticmethod(partial(yaml.dump, indent=2,
                                 default_flow_style=False))


class INI(object):
    @staticmethod
    def load(file):
        config = ConfigParser(allow_no_value=True)
        content = file.read().decode('utf-8')
        config.read_string(content)
        return config._sections

    @staticmethod
    def dumps(obj):
        buf = StringIO()
        config = ConfigParser(allow_no_value=True)  # noqa
        config.read_dict(obj)
        config.write(buf)
        return buf.getvalue()
