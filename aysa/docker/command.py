# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/12
# ~

from inspect import getdoc
from docopt import docopt, DocoptExit


CONST_COMMAND = 'COMMAND'
CONST_SERVICE = 'SERVICE'
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
        self.parent = kwargs.pop('parent', None)

    def get_doc(self):
        return getdoc(self)

    def get_docopt(self, *args, **kwargs):
        return docopt_helper(self.get_doc(), *args, **kwargs)

    def find_subcommand(self):
        raise NotImplementedError()

    def execute(self):
        raise NotImplementedError()


class NoSuchCommand(Exception):
    def __init__(self, command):
        super(NoSuchCommand, self).__init__("No such command: %s" % command)
        self.command = command
