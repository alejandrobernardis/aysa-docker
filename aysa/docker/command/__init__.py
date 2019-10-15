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
        docstring = docstring_helper(self)
        options = docopt_helper(docstring, argv, *args, **kwargs)
        command = options[CONST_COMMAND]

        if not hasattr(self, command):
            raise NoSuchCommand(command)

        handler = getattr(self, command)
        handler_docs = docstring_helper(handler)
        handler_opts = docopt_helper(handler_docs, options['ARGS'], 
                                     options_first=True)
        print(handler_opts)

    def __call__(self, argv=None, *args, **kwargs):
        return self.parse(argv, *args, **kwargs)

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        exit_code = 0
        if exc_val is not None:
            exit_code = 1
            print(exc_val)
        sys.exit(exit_code)


class NoSuchCommand(Exception):
    def __init__(self, command):
        super(NoSuchCommand, self).__init__("No such command: %s" % command)
        self.command = command
