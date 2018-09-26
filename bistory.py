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
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import has_focus
from prompt_toolkit.key_binding import KeyBindings


__version__ = '1.1.0'


class HistoryCompleter(Completer):
    def __init__(self):
        self._hist_file = os.getenv('HISTFILE', '~/.bash_history')

        self._history = None

    @property
    def history(self):
        if self._history:
            return self._history

        with open(os.path.expanduser(self._hist_file), 'rb') as f:
            self._history = b''.join(l for l in f.readlines()[::-1]
                                     if not l.startswith(b'#'))

        return self._history

    def _search(self, text):
        line = '.*'.join(re.escape(w) for w in text.split())
        _text = b'^(?<!#)(.*)(%s)(.*)$' % line.encode()

        matches = re.finditer(_text, self.history, flags=re.I | re.M)
        for _ in range(25):
            try:
                match = next(matches)
            except StopIteration:
                break
            else:
                yield match.group().decode()

    def get_completions(self, document, complete_event):
        for match in self._search(document.text):
            yield Completion(match, -document.cursor_position)


def main():
    key_bindings = KeyBindings()
    default_focused = has_focus(DEFAULT_BUFFER)

    # Autocomplete with backspace
    @key_bindings.add('backspace', filter=default_focused)
    def _(event):
        event.current_buffer.delete_before_cursor()
        event.current_buffer.insert_text('')

    session = PromptSession(
        wrap_lines=False,
        completer=HistoryCompleter(),
        key_bindings=key_bindings,
    )
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
