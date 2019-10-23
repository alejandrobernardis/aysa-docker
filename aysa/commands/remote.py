# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/21
# ~

# TODO i0608156: implementar un esquema de paralelismo para la ejecución de los
#                entornos. https://docs.fabfile.org/en/1.11/usage/parallel.html

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
            env = self.env_copy[stage]
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

    @lru_cache()
    def _norm_service(self, value, sep='_'):
        return sep.join(value.split(sep)[1:-1])

    def _list_to_str(self, values, sep=' '):
        return sep.join((x for x in values))

    def _list(self, cmd, filter_line=None, obj=None):
        response = self.run(cmd, hide=True)
        for line in response.stdout.splitlines():
            if filter_line and not filter_line.match(line):
                continue
            yield obj(line) if obj is not None else line

    def _list_environ(self, values, cnx=True):
        environs = [x for x in self._stages if values.get('--' + x, False)]
        for x in environs or (DEVELOPMENT,):
            if cnx is True:
                self.s_connection(x)
            stage = self.env[self._stage]
            self.output.head(x.upper(), stage.user, stage.host,
                             tmpl='[{}]: {}@{}', title=False)
            with self.cnx.cd('' if stage.user == '0x00' else stage.path):
                yield x
            self.output.blank()

    def _list_service(self, values=None, **kwargs):
        for x in self._list("docker-compose ps --services", rx_service):
            if values and x not in values:
                continue
            yield x

    def _services(self, values):
        if isinstance(values, dict):
            values = values['service']
        return [x for x in self._list_service(values)]

    def _deploy(self, **kwargs):
        # 1. detener los servicios
        self.run('docker-compose stop')

        # 2. buscar los servicios
        services = self._services(kwargs)

        # 3. buscar los contenedore e imágenes
        images = []

        for line in self._list("docker-compose images", rx_item):
            container, image, tag = line.split()[:3]
            if services and self._norm_service(container) not in services:
                continue
            images.append('{}:{}'.format(image, tag))

        # 4. eliminar los servicios
        try:
            if services:
                srv = self._list_to_str(set(services))
                self.run('docker-compose rm -fsv {}'.format(srv))
        except:
            pass

        # 5. eliminar las imágenes
        try:
            if images:
                srv = self._list_to_str(set(images))
                self.run('docker rmi -f {}'.format(srv))
        except:
            pass

        # 6. purgamos los volumenes
        self.run('docker volume prune -f')

        # 7. deplegar
        self.run('docker-compose up -d --remove-orphans')


class RemoteCommand(_ConnectionCommand):
    """
    Despliega las `imágenes` en los entornos de `DESARROLLO` y `QA/TESTING`.

    Usage: remote COMMAND [ARGS...]

    Comandos disponibles:
        down    Detiene y elimina los servicios en uno o más entornos.
        ls      Lista los servicios disponibles.
        prune   Purga los servicios en uno o más entornos.
        ps      ----
        restart Detiene y elimina los servicios en uno o más entornos.
        start   Inicia los servicios en uno o más entornos.
        stop    Detiene los servicios en uno o más entornos.
        up      Crea e inicia los servicios en uno o más entornos.
    """
    def up(self, **kwargs):
        """
        Crea e inicia los servicios en uno o más entornos.

        Usage: up [options] [SERVICE...]

        Opciones
            -d, --development       Entorno de `DESARROLLO`
            -q, --quality           Entorno de `QA/TESTING`
            -y, --yes               Responde "SI" a todas las preguntas.
        """
        if self.yes(**kwargs):
            for _ in self._list_environ(kwargs):
                self._deploy(**kwargs)


    def down(self, **kwargs):
        """
        Crea e inicia los servicios en uno o más entornos.

        Usage: down [options]

        Opciones
            -d, --development       Entorno de `DESARROLLO`
            -q, --quality           Entorno de `QA/TESTING`
            -y, --yes               Responde "SI" a todas las preguntas.
        """
        if self.yes(**kwargs):
            for _ in self._list_environ(kwargs):
                self.run('docker-compose down -v --remove-orphans')

    def start(self, **kwargs):
        """
        Inicia los servicios en uno o más entornos.

        Usage: start [options] [SERVICE...]

        Opciones
            -d, --development       Entorno de `DESARROLLO`
            -q, --quality           Entorno de `QA/TESTING`
            -y, --yes               Responde "SI" a todas las preguntas.
        """
        if self.yes(**kwargs):
            for _ in self._list_environ(kwargs):
                services = self._list_to_str(self._services(kwargs))
                self.run('docker-compose start {}'.format(services))

    def stop(self, **kwargs):
        """
        Detiene los servicios en uno o más entornos.

        Usage: stop [options] [SERVICE...]

        Opciones
            -d, --development       Entorno de `DESARROLLO`
            -q, --quality           Entorno de `QA/TESTING`
            -y, --yes               Responde "SI" a todas las preguntas.
        """
        if self.yes(**kwargs):
            for _ in self._list_environ(kwargs):
                services = self._list_to_str(self._services(kwargs))
                self.run('docker-compose stop {}'.format(services))

    def restart(self, **kwargs):
        """
        Detiene los servicios en uno o más entornos.

        Usage: restart [options] [SERVICE...]

        Opciones
            -d, --development       Entorno de `DESARROLLO`
            -q, --quality           Entorno de `QA/TESTING`
            -y, --yes               Responde "SI" a todas las preguntas.
        """
        if self.yes(**kwargs):
            for _ in self._list_environ(kwargs):
                services = self._list_to_str(self._services(kwargs))
                self.run('docker-compose restart {}'.format(services))

    def prune(self, **kwargs):
        """
        Purga los servicios en uno o más entornos.

        Usage: prune [--yes] (--development|--quality)

        Opciones
            -d, --development       Entorno de `DESARROLLO`
            -q, --quality           Entorno de `QA/TESTING`
            -y, --yes               Responde "SI" a todas las preguntas.
        """
        if self.yes(**kwargs):
            for _ in self._list_environ(kwargs):
                self.run('docker-compose down -v --rmi all --remove-orphans')
                self.run('docker volume prune -f')

    def ls(self, **kwargs):
        """
        Lista los servicios disponibles.

        Usage: ls [options]

        Opciones
            -d, --development       Entorno de `DESARROLLO`
            -q, --quality           Entorno de `QA/TESTING`
        """
        for _ in self._list_environ(kwargs):
            for line in self._list_service():
                self.output.bullet(line, tab=1)

    def ps(self, **kwargs):
        """
        Lista los servicios disponibles.

        Usage: ps [options]

        Opciones
            -d, --development       Entorno de `DESARROLLO`
            -q, --quality           Entorno de `QA/TESTING`
        """
        for _ in self._list_environ(kwargs):
            self.run("docker-compose ps")
