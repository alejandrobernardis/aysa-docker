# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/13
# ~

import sys
from docopt import docopt, DocoptExit
from inspect import getdoc, isclass
from functools import lru_cache
from pathlib import Path
from configparser import ConfigParser, ExtendedInterpolation

CONST_COMMAND = 'COMMAND'
CONST_ARGS = 'ARGS'


def docopt_helper(docstring, *args, **kwargs):
    try:
        if not isinstance(docstring, str):
            docstring = getdoc(docstring)
        return docopt(docstring, *args, **kwargs), docstring
    except DocoptExit:
        raise SystemExit(docstring)


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


class ConfigObject(ConfigParser):
    def to_dict(self):
        result = {}
        for sk, sv in self.items():
            if sk == 'common':
                continue
            for svk, svv in sv.items():
                if sk not in result:
                    result[sk] = AttrDict()
                result[sk][svk] = svv
        return AttrDict(result)


def env_helper(filename=None):
    filepath = Path(filename or '~/.aysa/config.ini').expanduser()
    parser = ConfigObject(interpolation=ExtendedInterpolation())
    if parser.read(filepath, encoding='utf-8'):
        return parser
    raise SystemExit('Es necesario definir el archivo "~/.aysa/config.ini", '
                     'con las configuración de los diferentes "endpoints": '
                     '`registry`, `development` y `quality`.')


class Command:
    def __init__(self, command, options=None, **kwargs):
        self.command = command
        self.options = options or {}
        self.options.setdefault('options_first', True)
        self.parent = kwargs.pop('parent', None)
        self._env = None

    @property
    def top_level(self):
        value = None
        while 1:
            if self.parent is None:
                return self
            elif value is None:
                value = self.parent
            elif value.parent is not None:
                value = value.parent
            else:
                break
        return value

    @property
    def global_options(self):
        return self.top_level.options

    @property
    def debug(self):
        return self.global_options.get('--debug', False)

    @property
    def verbose(self):
        return self.global_options.get('--verbose', False)

    @property
    def env_file(self):
        return self.global_options.get('--env', None)

    @property
    def env(self):
        return self.top_level._env

    @env.setter
    def env(self, value):
        self.top_level._env = value

    def parse(self, argv=None, *args, **kwargs):
        opt, doc = docopt_helper(self, argv, *args, **self.options, **kwargs)
        cmd = opt.pop(CONST_COMMAND)
        arg = opt.pop(CONST_ARGS)
        self.options.update(opt)

        try:
            scmd = self.find_command(cmd)
            sdoc = getdoc(scmd)
        except:
            raise SystemExit(doc)

        try:
            if isclass(scmd):
                sargs = arg[1:] if len(arg) > 1 else []
                scmd(cmd, parent=self).execute(arg[0], sargs, self.options)
            else:
                self.execute(scmd, arg, self.options, parent=self)
            return
        except Exception as e:
            if isinstance(e, CommandExit):
                raise e
        raise SystemExit(sdoc)

    def execute(self, command, args=None, global_args=None, **kwargs):
        if isinstance(command, str):
            command = self.find_command(command)

        hdr_opt, hdr_doc = docopt_helper(command, args, options_first=True)
        hdr_opt = {k.lower(): v for k, v in hdr_opt.items()}
        self.env = env_helper(self.env_file).to_dict()

        try:
            command(**hdr_opt, global_args=global_args)
        except Exception as e:
            raise CommandExit(hdr_doc)

    def find_command(self, command):
        try:
            if hasattr(self, 'commands'):
                return getattr(self, 'commands')[command]
            return getattr(self, command)
        except:
            pass
        raise NoSuchCommand(command)

    def __call__(self, argv=None, *args, **kwargs):
        return self.parse(argv, *args, **kwargs)

    def __str__(self):
        return '<Command="{}">'.format(self.command)


class NoSuchCommand(Exception):
    def __init__(self, command):
        super().__init__("No such command: %s" % command)
        self.command = command


class CommandExit(SystemExit):
    def __init__(self, docstring):
        super().__init__(docstring)
        self.docstring = docstring
