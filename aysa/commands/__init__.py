# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/18
# ~

import sys
import json
from pathlib import Path
from functools import lru_cache
from docopt import docopt, DocoptExit
from inspect import getdoc, isclass
from configparser import ConfigParser, ExtendedInterpolation

CONST_COMMAND = 'COMMAND'
CONST_ARGS = 'ARGS'


def docopt_helper(docstring, *args, **kwargs):
    try:
        if not isinstance(docstring, str):
            docstring = getdoc(docstring)
        return docopt(docstring, *args, **kwargs), docstring
    except DocoptExit:
        raise CommandExit(docstring)


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
    raise CommandExit('Es necesario definir el archivo "~/.aysa/config.ini", '
                      'con las configuración de los diferentes "endpoints": '
                      '`registry`, `development` y `quality`.')


class Command:
    def __init__(self, command, options=None, **kwargs):
        self.output = Printer()
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
            raise CommandExit(doc)

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
        raise CommandExit(sdoc)

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

        self.done()

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

    def done(self):
        self.output.done()


class NoSuchCommand(Exception):
    def __init__(self, command):
        super().__init__("No such command: %s" % command)
        self.command = command


class CommandExit(SystemExit):
    def __init__(self, docstring):
        super().__init__(docstring)
        self.docstring = docstring


class Printer:
    def __init__(self, output=None):
        self.output = output or sys.stdout

    def _parse(self, *values, sep=' ', end='\n', endx=None, **kwargs):
        tmpl = kwargs.pop('tmpl', None)
        if tmpl is not None:
            value = tmpl.format(*values)
        else:
            value = sep.join([str(x) for x in values])
        if kwargs.pop('title', False):
            value = value.title()
        if kwargs.pop('lower', False):
            value = value.lower()
        if kwargs.pop('upper', False):
            value = value.upper()
        end = '\n' if not end and endx else end
        if end and (not value.endswith(end) or endx is not None):
            return '{}{}'.format(value, end * (endx or 1))
        return value

    def done(self):
        self.flush('Done.', endx=3)

    def error(self, *message, **kwargs):
        kwargs['icon'] = '!'
        self.bullet(*message, **kwargs)

    def title(self, *message, **kwargs):
        kwargs['icon'] = '~'
        self.bullet(*message, title=True, **kwargs)

    def head(self, *message, **kwargs):
        self.blank()
        self.title(*message, **kwargs)
        self.rule()

    def foot(self, *message, **kwargs):
        self.blank()
        self.rule()
        self.done()

    def rule(self, icon='-', maxsize=2):
        self.flush(icon * min(80, max(0, maxsize)))

    def question(self, *message, **kwargs):
        kwargs['icon'] = '?'
        self.bullet(*message, **kwargs)

    def bullet(self, *message, icon='>', **kwargs):
        if 'tmpl' in kwargs:
            kwargs['tmpl'] = '{} ' + kwargs['tmpl']
        self.write(icon, *message, **kwargs)

    def blank(self):
        self.flush('')

    def write(self, *values, **kwargs):
        value = self._parse(*values, **kwargs)
        if value:
            self.output.write(value)

    def flush(self, *values, **kwargs):
        if values:
            self.write(*values, **kwargs)
        self.output.flush()

    def json(self, value, indent=2):
        raw = json.dumps(value, indent=indent) \
              if isinstance(value, dict) else '-'
        self.output.write(raw + '\n')
        self.flush()
