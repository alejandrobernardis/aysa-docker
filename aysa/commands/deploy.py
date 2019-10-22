# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/21
# ~

import re
from pathlib import Path
from functools import lru_cache
from fabric import Connection
from aysa.commands import Command


rx_item = re.compile(r'^[a-z](?:[\w_])+_\d{1,3};[a-z0-9](?:[\w.-]+)(?::\d{1,5})'
                     r'?/[a-z0-9](?:[\w.-/])*(?::[a-z][\w.-]*)', re.I)
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
        return self.cnx.run(command, hide=hide, **kwargs)

    def _list(self, cmd, filter_line=None, obj=None):
        response = self.cnx.run(cmd, hide=True)
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
        services = []

        # 1. detener los servicios
        self.run('docker-compose stop')

        # 2. buscar los servicios
        cmd = "docker-compose ps --services"
        service = [x for x in self._list(cmd, rx_service)
                      if x in kwargs['service']]

        # 3. buscar los contenedore e imágenes
        cmd = "docker-compose images | awk '{print $1 \";\" $2 \":\" $3}'"

        for line in self._list(cmd, rx_item):
            container, _, image = line.partition(';')
            container_service = self._get_service(container)
            if service and container_service not in service:
                continue
            services.append((container_service, image))
            self.output.write(line)

        # 4. eliminar los servicios
        try:
            self.run('yes | docker-compose rm {}'
                     .format(' '.join((x[0] for x in services))))
        except:
            pass

        # 5. eliminar las imágenes
        try:
            self.run('yes | docker rmi -f {}'
                     .format(' '.join((x[1] for x in services))))
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
