# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/21
# ~

"""
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
"""

import re
from pathlib import Path
from fabric import Connection
from aysa.commands import Command
from aysa.docker.registry import Image
from functools import partial, partialmethod

# rx_service = re.compile(r'^[a-z](?:[\w_])+$', re.I)
# rx_image = re.compile(r'^(localhost|[\w\-]+(\.[\w\-]+)+)(?::\d{1,5})?\/', re.I)
# rx_container = re.compile(r'^[a-z](?:[\w_])+\d{1,3}$', re.I)


class _ConnectionCommand(Command):
    def execute(self, command, argv=None, global_args=None, **kwargs):
        super().execute(command, argv, global_args, **kwargs)
        self.cnx.close()

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
            self._connection_cache = Connection(**env)
        return self._connection_cache

    @property
    def cnx(self):
        return self._connection_cache

    def run(self, command, hide=False, **kwargs):
        #return self.cnx.run(command, hide=hide, **kwargs)
        print(command)

    def _list(self, cmd, filter_line=None, obj=None):
        response = self.cnx.run(cmd, hide=True)
        for line in response.stdout.splitlines():
            if filter_line and not filter_line.match(line):
                continue
            yield obj(line) if obj is not None else line

    _services = partialmethod(
        _list,
        cmd="docker-compose images | awk '{print $1 \";\" $2 \":\" $3}'",
        filter_line=None
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
        services = []
        cnx = self._connection()
        service = kwargs['service']

        # 1. detener los servicios
        #  >> docker-compose stop
        self.run('docker-compose stop')

        # 2. buscar los servicios y sus imágenes
        #  >> docker-compose images | awk '{print $1 ";" $2 ":" $3}'
        lines = self.run("docker-compose images "
                         "| awk '{print $1 \";\" $2 \":\" $3}'")
        # for line in lines.stdout.splitlines():
        #     container, _, image = line.partition(';')
        #     services.append((container, image))

        # 3. eliminar los servicios
        #  >> docker-compose rm [service...]
        self.run('docker-compose rm {}'
                 .format(' '.join((x[0] for x in services))))

        # 4. eliminar las imágenes
        #  >> docker rmi -f $()
        self.run('docker-compose rmi -f {}'
                 .format(' '.join((x[1] for x in services))))

        # 5. deplegar
        #  >> docker-compose up -d
        self.run('docker-compose up -d')

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
