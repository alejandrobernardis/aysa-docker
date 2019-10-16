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
        return docopt(docstring, *args, **kwargs), docstring
    except DocoptExit:
        raise SystemExit(docstring)


def docstring_helper(value):
    return '\n%s\n' % getdoc(value)


class Command:
    def __init__(self, command, options=None, **kwargs):
        self.command = command
        self.options = options or {}
        self.options.setdefault('options_first', True)
        self.parent = kwargs.pop('parent', None)

    def top_level(self):
        value = None
        while 1:
            if value is None:
                value = self.parent
            elif value.parent is not None:
                value = value.parent
            else:
                break
        return value

    def parse(self, argv=None, *args, **kwargs):
        opt, doc = docopt_helper(self, argv, *args, **self.options, **kwargs)
        cmd = opt.pop(CONST_COMMAND)
        arg = opt.pop(CONST_ARGS)

        if cmd is None:
            raise SystemExit(doc)

        self.options.update(opt)

        hdr = self.find_command(cmd)
        hdr_opt, hdr_doc = docopt_helper(hdr, arg)
        print(hdr, hdr_opt)
        # handler(**{k.lower(): v for k, v in handler_opts.items()})

    def execute(self, command, args=None, **kwargs):
        # kwargs.setdefault('options_first', True)
        # handler = self.find_command(command)
        # options = docopt_helper(handler, args, **kwargs)
        # handler(**options)
        pass

    def find_command(self, command):
        if command is None or not hasattr(self, command):
            raise NoSuchCommand(command)
        return getattr(self, command)

    def __call__(self, argv=None, *args, **kwargs):
        return self.parse(argv, *args, **kwargs)


class NoSuchCommand(Exception):
    def __init__(self, command):
        super(NoSuchCommand, self).__init__("No such command: %s" % command)
        self.command = command
