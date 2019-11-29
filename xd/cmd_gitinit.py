# -*- coding: utf-8 -*-

import os
import sys
from os import path as pathlib
import subprocess
from datetime import datetime

import click
import requests
from six import text_type

from .__version__ import __version__
from .helpers import ClickListOption, abort, err_abort, cd


_HEADERS = {'User-Agent': 'xd/{}'.format(__version__)}
_GITHUB_API_HEADERS = {'Accept': 'application/vnd.github.v3.raw+json'}
_GITHUB_API_HEADERS.update(_HEADERS)
_LICENSE_URL = 'https://api.github.com/licenses/{}'
# https://developer.github.com/v3/gitignore/
_GLOBAL_GITIGNORE_URL = 'https://raw.githubusercontent.com/github/gitignore/master/Global/{}.gitignore'  # noqa
_GITIGNORE_URL = 'https://raw.githubusercontent.com/github/gitignore/master/{}.gitignore'  # noqa
_PLATFORM_MAP = {
    'linux': 'Linux',
    'darwin': 'macOS',
    'win32': 'Windows',
    'cygwin': 'Windows',
}


@click.command(name='gitinit')
@click.option('-p', '--path', default='.', show_default=True,
              help=('Project path, if `only` is presented,'
                    ' it is the path for license or gitignore file'))
@click.option('-l', '--license', type=str, default='', show_default=True,
              help='https://help.github.com/articles/licensing-a-repository/#searching-github-by-license-type')  # noqa
@click.option('-i', '--gitignores', cls=ClickListOption, show_default=True,
              help=('Comma-separated list of gitignore template types.'
                    'It will add platform specified template automatically'
                    ' unless `only` and `append` flag are both presented.'))
@click.option('-o', '--only', is_flag=True, default=False, show_default=True,
              help='Use it to only modify license or gitignore.')
@click.option('-a', '--append', is_flag=True, default=False, show_default=True,
              help='Co-operate with `gitignore`, otherwise it is ignored')
def command(path, license, gitignores, only, append):
    """
    Init a git project, or creates a LICENSE/.gitignore file.

        xd gitinit -p pro -l mit -i Python  # init a porject

        xd gitinit -o -l bsd-3-clause       # creat or overwrite a LICENSE

        xd gitinit -o -a -i Swift,Xcode     # append to or create a .gitignore
    """
    nothing = not license and not gitignores
    if only and (nothing or all((license, gitignores))):
        abort('--only should work with --license or --gitignores')
    if not only and (nothing or (not license or not gitignores)):
        abort('--license and --gitignores required')
    if not only:
        ensure_dir(path)
        with cd(path):
            step_license(license, '.')
            step_gitignore(gitignores, '.', not append)
            init_git()
    elif license:
        step_license(license, path)
    elif gitignores:
        step_gitignore(gitignores, path, not append)


def step_license(typ, fpath):
    fpath = _complete_path(fpath, 'LICENSE')

    with requests.Session() as session:
        resp = session.get(
            _LICENSE_URL.format(typ), headers=_GITHUB_API_HEADERS, timeout=5)
        if resp.status_code != 200:
            abort(
                'fetching {} license failed with: {} {}',
                typ, resp.status_code, resp.reason
            )
        license = resp.json()['body']

    year = str(datetime.today().year)
    fullname = _git_fullname()
    license = license.replace('[year]', year).replace('[fullname]', fullname)
    _write([license], fpath, True)


def step_gitignore(types, fpath, overwrite):
    fpath = _complete_path(fpath, '.gitignore')
    platform = _PLATFORM_MAP[sys.platform]
    gitignore_tpls = []

    with requests.Session() as session:
        session.headers.update(_HEADERS)
        if overwrite:
            resp = session.get(
                _GLOBAL_GITIGNORE_URL.format(platform), timeout=5)
            if resp.status_code != 200:
                abort(
                    'fetching {}.gitignore failed with: {} {}',
                    platform, resp.status_code, resp.reason
                )
            gitignore_tpls.extend(['## {}\n'.format(platform), resp.content])

        for typ in types:
            resp = session.get(_GITIGNORE_URL.format(typ), timeout=5)
            if resp.status_code == 404:
                resp = session.get(
                    _GLOBAL_GITIGNORE_URL.format(typ), timeout=5)
            if resp.status_code != 200:
                abort(
                    'fetching {}.gitignore failed with: {} {}',
                    typ, resp.status_code, resp.reason
                )
            gitignore_tpls.extend(['\n\n## {}\n'.format(typ), resp.content])

    _write(gitignore_tpls, fpath, overwrite)


def ensure_dir(fpath):
    if not pathlib.isdir(fpath):
        os.makedirs(fpath)


def init_git(_cmd=['git', 'init']):
    with err_abort('execute `git init` failed'):
        subprocess.check_call(_cmd)


def _complete_path(fpath, filename):
    if pathlib.isdir(fpath):
        return pathlib.join(fpath, filename)
    return fpath


def _write(contents, fpath, overwrite):
    mode = 'wb' if overwrite else 'ab'

    with err_abort('write {} failed', fpath):
        with open(fpath, mode) as f:
            for content in contents:
                if isinstance(content, text_type):
                    content = content.encode('utf-8')
                f.write(content)


def _git_fullname():
    git_user_name_cmd = 'git config --global user.name'.split()
    git_user_email_cmd = 'git config --global user.email'.split()
    with err_abort('get user name and email failed'):
        name = subprocess.check_output(git_user_name_cmd)
        email = subprocess.check_output(git_user_email_cmd)

    fullname = '[fullname]'
    if name:
        fullname = name.decode('utf-8').strip()
    if email:
        fullname += ' <{}>'.format(email.decode('utf-8').strip())
    return fullname
