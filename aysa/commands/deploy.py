# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/21
# ~

import re
from pathlib import Path
from functools import lru_cache
from fabric import Connection
from aysa.commands import Command


rx_item = re.compile(r'^[a-z](?:[\w_])+_\d{1,3}\s{2,}[a-z0-9](?:[\w.-]+)(?::\d{1,5})'
                     r'?/[a-z0-9](?:[\w.-/])*\s{2,}(?:[a-z][\w.-]*)\s', re.I)
rx_service = re.compile(r'^[a-z](?:[\w_])+$', re.I)


class _ConnectionCommand(Command):
    def execute(self, command, argv=None, global_args=None, **kwargs):
        super().execute(command, argv, global_args, **kwargs)
        self.cnx.close()

    _stage = None
    _connection_cache = None

    def _connection(self, stage=None):
        if self._connection_cache is None:
            env = self.env[stage]
            if env['user'].lower() == 'root':
                raise SystemExit('El usuario "root" no está permitido para '
                                 'ejecutar despliegues.')
            pkey = Path(env.pop('pkey', None)).expanduser()
            env['connect_kwargs'] = {'key_filename': str(pkey)}
            self._connection_cache = Connection(**env)
            self._stage = stage
        return self._connection_cache

    @property
    def cnx(self):
        if self._stage and self._connection_cache is None:
            self._connection(self._stage)
        return self._connection_cache

    def run(self, command, hide=False, **kwargs):
        self.output.bullet(command)
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


class DeployCommand(_ConnectionCommand):
    """
    Despliega las `imágenes` en los entornos de `DESARROLLO` y `QA/TESTING`.

    Usage: deploy COMMAND [ARGS...]

    Comandos disponibles:
        deve    Despliegue en el entorno de `DESARROLLO`.
        test    Despliegue en el entorno de `QA/TESTING`.
    """
    def _deploy(self, stage, **kwargs):
        # establecemos la conexión
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
        cmd = "docker-compose images " # | awk '{print $1 \";\" $2 \":\" $3}'"

        for line in self._list(cmd, rx_item):
            container, image, tag = line.split()[:3]
            if services and self._get_service(container) not in services:
                continue
            images.append('{}:{}'.format(image, tag))

        # # 4. eliminar los servicios
        try:
            srv = ' '.join((x for x in service))
            self.run('yes | docker-compose rm {}'.format(srv))
        except:
            pass

        # # 5. eliminar las imágenes
        try:
            srv = ' '.join((x for x in images))
            self.run('yes | docker rmi -f {}'.format(srv))
        except:
            pass

        # 6. deplegar
        self.run('docker-compose up -d')

    def deve(self, **kwargs):
        """
        Despliegue en el entorno de `DESARROLLO`.

        Usage: deve [SERVICE...]
        """
        self._deploy('development', **kwargs)

    def test(self, **kwargs):
        """
        Despliegue en el entorno de `QA/TESTING`.

        Usage: test [SERVICE...]
        """
        self._deploy('quality', **kwargs)


class ServiceCommand(_ConnectionCommand):
    """
    ...

    Usage: service COMMAND [ARGS...]

    Comandos disponibles:
        ls         ...
        ps         ...
        stop       ...
        start      ...
        restart    ...
    """
