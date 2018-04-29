# -*- coding: utf-8 -*-

import threading
import subprocess
import signal

from click import echo
from colorama import init, Fore, Style
init(autoreset=True)


out_lock = threading.Lock()
color_funcs = []


def append_color_func(color):
    def output(line, pid=''):
        if pid:
            pid = '{0}{1}{2}{3}: {0}'.format(
                color, Style.BRIGHT, pid, Style.RESET_ALL)
        with out_lock:
            echo(''.join((pid, color, line)), nl=False)
    color_funcs.append(output)


append_color_func('')
for name in dir(Fore):
    if not name.startswith('_') and name not in ('BLACK', 'RESET'):
        append_color_func(getattr(Fore, name))


class Proc(subprocess.Popen):

    def __init__(self, cmd, color_idx=0, rule=None):
        super(self.__class__, self).__init__(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
            close_fds=True,
        )

        self._print = color_funcs[color_idx % len(color_funcs)]
        with_pid = color_idx != 0
        self._log_t = threading.Thread(
            target=self._record_log,
            args=(with_pid, rule))
        self._log_t.start()

    def _record_log(self, with_pid, rule):
        pid = str(self.pid) if with_pid else ''
        for line in self.stdout:
            self._print(line, pid)

    def wait(self, timeout=None):
        super(self.__class__, self).wait(timeout)
        self._log_t.join()


def register_signal_handler(handler):
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


__signum2str = {
    k: v for v, k in sorted(signal.__dict__.items())
    if v.startswith('SIG') and not v.startswith('SIG_')
}


def signum2str(signum, default='unknown'):
    return __signum2str.get(signum, default)
