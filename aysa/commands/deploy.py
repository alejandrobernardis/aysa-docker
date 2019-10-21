# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/21
# ~

import re
from pathlib import Path
from fabric import Connection
from aysa.commands import Command
from aysa.docker.registry import Image
from functools import partial, partialmethod

rx_service = re.compile(r'^[a-z](?:[\w_])+$', re.I)
rx_image = re.compile(r'^(localhost|[\w\-]+(\.[\w\-]+)+)(?::\d{1,5})?\/', re.I)
rx_container = re.compile(r'^[a-z](?:[\w_])+\d{1,3}$', re.I)


class ConnectionHelper:
    def __init__(self, connection, auto_close=False):
        self.connection = connection
        self.auto_close = auto_close

    def close(self):
        if self.connection is not None:
            self.connection.close()

    def __enter__(self, ):
        if self.connection is None:
            raise SystemExit('No se estableció la conexión con el servidor.')
        return self.connection

    def __exit__(self, *exc):
        if self.auto_close is True:
            self.close()


class _ConnectionCommand(Command):
    _stage = None
    _connection_cache = None

    def _connection(self, stage=None):
        if self._connection_cache is None:
            env = self.env[stage or self._stage]
            if env['user'].lower() == 'root':
                raise SystemExit('El usuario "root" no está permitido para '
                                 'ejecutar despliegues.')
            pkey = Path(env.pop('pkey', None)).expanduser()
            env['connect_kwargs'] = {'key_filename': str(pkey)}
            self._connection_cache = ConnectionHelper(Connection(**env))
        return self._connection_cache

    @property
    def cnx(self):
        return self._connection_cache.connection

    def _list(self, cmd, filter_line=None, obj=None):
        with self._connection() as cx:
            response = cx.run(cmd, hide=True)
            for line in response.stdout.splitlines():
                if filter_line and not filter_line.match(line):
                    continue
                yield obj(line) if obj is not None else line

    _images = partialmethod(
        _list,
        cmd="docker-compose images | awk '{print $2 \":\" $3}'",
        filter_line=rx_image,
        obj=Image
    )

    _services = partialmethod(
        _list,
        cmd="docker-compose ps --services",
        filter_line=rx_service
    )

    _running = partialmethod(
        _list,
        cmd="docker-compose ps | grep -P '\s{2,}Up' | awk '{print $1}'",
        filter_line=rx_container
    )


class DeployCommand(_ConnectionCommand):
    """
    Despliega las `imágenes` en los entornos de `DESARROLLO` y `QA/TESTING`.

    Usage: deploy COMMAND [ARGS...]

    Comandos disponibles:
        deve    Despliegue en el entorno de `DESARROLLO`.
        test    Despliegue en el entorno de `QA/TESTING`.
    """
    def _deploy(self, **kwargs):
        service = kwargs['service']
        for x in self._running(stage):
            self.output.write(x)

    def deve(self, **kwargs):
        """
        Despliegue en el entorno de `DESARROLLO`.

        Usage: deve [SERVICE...]
        """
        self._stage = 'development'
        self._deploy(**kwargs)

    def test(self, **kwargs):
        """
        Despliegue en el entorno de `QA/TESTING`.

        Usage: test [SERVICE...]
        """
        self._stage = 'quality'
        self._deploy(**kwargs)


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
