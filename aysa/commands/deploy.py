# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/21
# ~

import re
from pathlib import Path
from functools import lru_cache
from fabric import Connection
from aysa.commands import Command

DEVELOPMENT = 'development'
QUALITY = 'quality'
rx_item = re.compile(r'^[a-z](?:[\w_])+_\d{1,3}\s{2,}[a-z0-9](?:[\w.-]+)'
                     r'(?::\d{1,5})?/[a-z0-9](?:[\w.-/])*\s{2,}'
                     r'(?:[a-z][\w.-]*)\s', re.I)
rx_service = re.compile(r'^[a-z](?:[\w_])+$', re.I)


class _ConnectionCommand(Command):
    _stage = None
    _stages = (DEVELOPMENT, QUALITY)
    _connection_cache = None

    def s_close(self):
        if self._connection_cache is not None:
            self._connection_cache.close()
            self._connection_cache = None
            self._stage = None

    def s_connection(self, stage=None):
        if self._stage and stage != self._stage:
            self.s_close()
        if self._connection_cache is None:
            env = self.env[stage]
            env.pop('path', None)
            if env['user'].lower() == 'root':
                raise SystemExit('El usuario "root" no está permitido para '
                                 'ejecutar despliegues.')
            pkey = Path(env.pop('pkey', None)).expanduser()
            env['connect_kwargs'] = {'key_filename': str(pkey)}
            self._connection_cache = Connection(**env)
            self._stage = stage
        return self._connection_cache

    def on_finish(self, *args, **kwargs):
        self.s_close()

    @property
    def cnx(self):
        if self._stage and self._connection_cache is None:
            self.s_connection(self._stage)
        return self._connection_cache

    def run(self, command, hide=False, **kwargs):
        return self.cnx.run(command, hide=hide, **kwargs)

    def _list(self, cmd, filter_line=None, obj=None):
        response = self.run(cmd, hide=True)
        for line in response.stdout.splitlines():
            if filter_line and not filter_line.match(line):
                continue
            yield obj(line) if obj is not None else line

    @lru_cache()
    def _get_service(self, value, sep='_'):
        return sep.join(value.split(sep)[1:-1])

    def _get_strlist(self, values, sep=' '):
        return sep.join((x for x in values))

    # def _get_environ(self, values):
    #     return (x for x in self._stages if values.get('--' + x, False))

    def _get_environ(self, values, cnx=True):
        for x in self._stages:
            if not values.get('--' + x, False):
                continue
            if cnx is True:
                self.s_connection(x)
            self.output.title(x)
            yield x
            self.output.blank()


class DeployCommand(_ConnectionCommand):
    """
    Despliega las `imágenes` en los entornos de `DESARROLLO` y `QA/TESTING`.

    Usage: deploy COMMAND [ARGS...]

    Comandos disponibles:
        ls      Lista los servicios disponibles.
        up      Crea e inicia los servicios en uno o más entornos.
        down    Detiene y elimina los servicios en uno o más entornos.
        prune   Purga los servicios en uno o más entornos.
    """
    def _deploy(self, stage, **kwargs):
        # establecemos la conexión
        if stage is not None:
            self._connection(stage)

        # servicios a purgar
        images = []
        services = []

        # 1. detener los servicios
        self.run('docker-compose stop')

        # 2. buscar los servicios
        cmd = "docker-compose ps --services"
        services = [x for x in self._list(cmd, rx_service)
                       if x in kwargs['service']]

        # 3. buscar los contenedore e imágenes
        cmd = "docker-compose images "

        for line in self._list(cmd, rx_item):
            container, image, tag = line.split()[:3]
            if services and self._get_service(container) not in services:
                continue
            images.append('{}:{}'.format(image, tag))

        # # 4. eliminar los servicios
        try:
            srv = self._get_strlist(services)
            self.run('yes | docker-compose rm {}'.format(srv))
        except Exception as e:
            pass

        # # 5. eliminar las imágenes
        try:
            srv = self._get_strlist(images)
            self.run('yes | docker rmi -f {}'.format(srv))
        except:
            pass

        # 6. deplegar
        self.run('docker-compose up -d')

    def up(self, **kwargs):
        """
        Crea e inicia los servicios en uno o más entornos.

        Usage: up [options] [SERVICE...]

        Opciones
            -d, --development       Entorno de `DESARROLLO`
            -q, --quality           Entorno de `QA/TESTING`
        """
        for x in self._get_environ(kwargs):
            self._deploy(None, **kwargs)

    def down(self, **kwargs):
        """
        Crea e inicia los servicios en uno o más entornos.

        Usage: down [options] [SERVICE...]

        Opciones
            -d, --development       Entorno de `DESARROLLO`
            -q, --quality           Entorno de `QA/TESTING`
        """
        for x in self._get_environ(kwargs):
            self.run('docker-compose down')

    def prune(self, **kwargs):
        """
        Purga los servicios en uno o más entornos.

        Usage: prune [options] [SERVICE...]

        Opciones
            -d, --development       Entorno de `DESARROLLO`
            -q, --quality           Entorno de `QA/TESTING`
        """
        for x in self._get_environ(kwargs):
            self.down(**kwargs)
            # self.run('docker rmi -f $(docker images -q)')


    def ls(self, **kwargs):
        """
        Lista los servicios disponibles.

        Usage: ls [options]

        Opciones
            -d, --development       Entorno de `DESARROLLO`
            -q, --quality           Entorno de `QA/TESTING`
        """
        for x in self._get_environ(kwargs):
            for line in self._list("docker-compose ps --services", rx_service):
                self.output.bullet(line, tab=1)

    def ps(self, **kwargs):
        """
        Lista los servicios disponibles.

        Usage: ps [options]

        Opciones
            -d, --development       Entorno de `DESARROLLO`
            -q, --quality           Entorno de `QA/TESTING`
        """
        for x in self._get_environ(kwargs):
            self.run("docker-compose ps")
