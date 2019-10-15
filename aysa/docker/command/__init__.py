# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/13
# ~

import sys
from aysa import EMPTY
from inspect import getdoc
from functools import lru_cache
from docopt import docopt, DocoptExit


CONST_COMMAND = 'COMMAND'
CONST_ARGS = 'ARGS'


def docopt_helper(docstring, *args, **kwargs):
    try:
        if not isinstance(docstring, str):
            docstring = docstring_helper(docstring)
        return docopt(docstring, *args, **kwargs)
    except DocoptExit:
        raise SystemExit(docstring)


def docstring_helper(value):
    return '\n%s\n\n' % getdoc(value)


class Command:
    def __init__(self, command, options=None, **kwargs):
        self.command = command
        self.options = options or {}
        self.options.setdefault('options_first', True)
        self.parent = kwargs.pop('parent', None)

    def parse(self, argv=EMPTY, *args, **kwargs):
        if argv is EMPTY:
            argv = sys.argv[1:]

        kwargs.update(self.options)
        options = docopt_helper(self, argv, *args, **kwargs)
        command = options[CONST_COMMAND]

        if not hasattr(self, command):
            raise NoSuchCommand(command)

        handler = getattr(self, command)
        handler_opts = docopt_helper(handler, options['ARGS'],
                                     options_first=True)
        print(handler_opts)
        handler()

    def __call__(self, argv=None, *args, **kwargs):
        return self.parse(argv, *args, **kwargs)


class NoSuchCommand(Exception):
    def __init__(self, command):
        super(NoSuchCommand, self).__init__("No such command: %s" % command)
        self.command = command
