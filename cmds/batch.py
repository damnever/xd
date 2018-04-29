# -*- coding: utf-8 -*-

import sys
import time

from .proc import Proc, register_signal_handler, signum2str


class Batch(object):
    _POLL_INTERVAL = 0.02
    _WAIT_BEFORE_KILL = 0.01  # TODO: make it configurable

    def __init__(self, cmd, count, step=1, interval=1, err_exit=True):
        self._cmd = cmd
        self._count = count
        self._step = step
        self._interval = interval
        self._err_exit = err_exit

        self._ps = None

        register_signal_handler(self.handle_signal)

    def run(self):
        n, rest = divmod(self._count, self._step)
        for i in range(self._step):
            if i != 0:
                time.sleep(self._interval)
            self.batch(n)
            self.wait(n)

        if rest > 0:
            self.batch(rest)
            self.wait(rest)

    def batch(self, n):
        self._ps = []

        for i in range(n):
            try:
                p = Proc(self._cmd, color_idx=i+1)
                self._ps.append(p)
            except Exception as e:
                self.exit(e)

    def wait(self, n):
        finished = 0

        while 1:
            current_finished, err_code = self.poll()
            if err_code != 0:
                self.exit()
            finished += current_finished

            if finished >= n:
                break
            time.sleep(self._POLL_INTERVAL)

        [p.wait() for p in self._ps]

    def poll(self):
        finished = 0
        err_code = 0

        for p in self._ps:
            if p.poll() is None:
                continue
            if self._err_exit and p.returncode != 0:
                err_code = p.returncode
                break
            finished += 1

        return finished, err_code

    def handle_signal(self, signum, frame):
        self.exit(' Exit with: ' + signum2str(signum))

    def exit(self, code=1):
        if not self._ps:
            sys.exit(code)
            return

        for p in self._ps:
            if p.poll() is None:
                p.terminate()

        time.sleep(self._WAIT_BEFORE_KILL)
        for p in self._ps:
            if p.poll() is None:
                p.kill()

        [p.wait() for p in self._ps]
        sys.exit(code)

    def __call__(self):
        self.run()
