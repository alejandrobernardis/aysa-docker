# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/13
# ~

import sys
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


class Command:
    def __init__(self, command, options=None, **kwargs):
        self.command = command
        self.options = options or {}
        self.options.setdefault('options_first', True)
        self.parent = kwargs.pop('parent', None)

    @property
    def is_toplevel(self):
        return self.command is None

    @lru_cache()
    def get_doc(self):
        return getdoc(self) + '\n'

    def get_docopt(self, *args, **kwargs):
        return docopt_helper(self.get_doc(), *args, **kwargs)

    def parse(self, argv, *args, **kwargs):
        options = self.get_docopt(argv, *args, **kwargs)
        command = options[CONST_COMMAND]

        if command is None or not hasattr(self, command):
            raise SystemExit(self.get_doc())

        getattr(self, command)(options)

    def __call__(self, argv, *args, **kwargs):
        return self.parse(argv, *args, **kwargs)

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is SystemExit:
            print(exc_val)
        sys.exit()


class NoSuchCommand(Exception):
    def __init__(self, command):
        super(NoSuchCommand, self).__init__("No such command: %s" % command)
        self.command = command
