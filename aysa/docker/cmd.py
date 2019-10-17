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
            docstring = getdoc(docstring)
        return docopt(docstring, *args, **kwargs), docstring
    except DocoptExit:
        raise SystemExit(docstring)


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

    def top_level_options(self):
        return self.top_level().options

    @property
    def debug(self):
        return self.top_level_options().get('--debug', False)

    @property
    def verbose(self):
        return self.top_level_options().get('--verbose', False)

    @property
    def env(self):
        return {}

    def parse(self, argv=None, *args, **kwargs):
        opt, doc = docopt_helper(self, argv, *args, **self.options, **kwargs)
        cmd = opt.pop(CONST_COMMAND)
        arg = opt.pop(CONST_ARGS)
        self.options.update(opt)

        if cmd is None:
            raise SystemExit(doc)
        
        hdr = self.find_command(cmd)
        hdr_opt, hdr_doc = docopt_helper(hdr, arg)
        hdr_opt = {k.lower(): v for k, v in hdr_opt.items()}
        hdr_opt.update({'global_args': self.options})
        hdr(hdr_opt)

    def execute(self, command, args=None, global_args=None, **kwargs):
        hdr = self.find_command(command)
        hdr_opt, hdr_doc = docopt_helper(hdr, args, options_first=True)
        hdr(**hdr_opt, global_args=global_args)

    def find_command(self, command):
        if command is None or not hasattr(self, command):
            raise NoSuchCommand(command)
        return getattr(self, command)

    def __call__(self, argv=None, *args, **kwargs):
        return self.parse(argv, *args, **kwargs)

    def __str__(self):
        return '<Command="{}">'.format(self.command)


class NoSuchCommand(Exception):
    def __init__(self, command):
        super(NoSuchCommand, self).__init__("No such command: %s" % command)
        self.command = command
