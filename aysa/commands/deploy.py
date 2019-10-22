# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/21
# ~

import re
from pathlib import Path
from fabric import Connection
from aysa.commands import Command


rx_line = re.compile(r'^[a-z](?:[\w_])+_\d{1,3};[a-z0-9](?:[\w.-]+)(?::\d{1,5})'
                     r'?/[a-z0-9](?:[\w.-/])*(?::[a-z][\w.-]*)', re.I)


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
        return self.cnx.run(command, hide=hide, **kwargs)

    def _list(self, cmd, filter_line=None, obj=None):
        response = self.cnx.run(cmd, hide=True)
        for line in response.stdout.splitlines():
            if filter_line and not filter_line.match(line):
                continue
            yield obj(line) if obj is not None else line


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
        services = []

        # 1. detener los servicios
        self.run('docker-compose stop')

        # 2. buscar los servicios y sus imágenes
        cmd = "docker-compose images | awk '{print $1 \";\" $2 \":\" $3}'"
        service = kwargs['service']

        for line in self._list(cmd, rx_line):
            container, _, image = line.partition(';')
            services.append((container, image))

        # 3. eliminar los servicios
        self.run('docker-compose rm {}'
                 .format(' '.join((x[0] for x in services))))

        # 4. eliminar las imágenes
        self.run('docker-compose rmi -f {}'
                 .format(' '.join((x[1] for x in services))))

        # 5. deplegar
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
