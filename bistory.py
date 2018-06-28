#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 Matt Martz
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import unicode_literals

import fcntl
import os
import re
import sys
import termios

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion

__version__ = '1.0.0'


class HistoryCompleter(Completer):
    def __init__(self):
        hist_file = os.getenv('HISTFILE', '~/.bash_history')

        with open(os.path.expanduser(hist_file), 'rb') as f:
            self._history = b''.join(l for l in f.readlines()[::-1])

    def _search(self, text):
        line = '.*'.join(re.escape(w) for w in text.split())
        _text = b'^(?<!#)(.*)(%s)(.*)$' % line.encode()

        matches = re.finditer(_text, self._history, flags=re.I | re.M)
        for _ in range(25):
            match = next(matches)
            yield match.group().decode()

    def get_completions(self, document, complete_event):
        for match in self._search(document.text):
            yield Completion(match, -document.cursor_position)


def main():
    session = PromptSession(wrap_lines=False, completer=HistoryCompleter())
    text = '%s\n' % session.prompt('> ')
    if text.strip():
        for c in text:
            fcntl.ioctl(sys.stdout, termios.TIOCSTI, c)


def shell():
    sys.stdout.write('\033[F')
    sys.stdout.flush()
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        sys.stdout.write('\033[F\033[K')
    else:
        sys.stdout.write('\033[F\033[K\033[F\033[K')


if __name__ == '__main__':
    shell()
