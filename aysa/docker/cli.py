# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/12
# ~
# -V, --verbose     Activa el modo `verbose`.

import sys
import logging
from aysa import __version__
from aysa.docker.api import Registry, Api, Image, get_parts
from aysa.docker.cmd import NoSuchCommand, Command


# logger
log = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stderr)


class RegistryCommand(Command):
    _registry_api = None

    @property
    def api(self):
        if self._registry_api is None:
            self._registry_api = Api(**self.env.registry)
        return self._registry_api

    @property
    def namespace(self):
        return self.env.registry.namespace

    def _fix_image_name(self, value, namespace=None):
        value = value.strip()
        namespace = namespace or self.namespace
        return '{}/{}'.format(namespace, value) \
            if not value.startswith(namespace) else value

    def _fix_images_list(self, values, namespace=None):
        values = values.split(',') if isinstance(values, str) else values or []
        return [self._fix_image_name(x.strip(), namespace) for x in values]

    def _fix_tags_list(self, values):
        if not values or values == '*':
            return '*'
        return [x.strip() for x in values.split(',')]

    def _list(self, filter_repos=None, filter_tags=None):
        filter_repos = self._fix_images_list(filter_repos)
        filter_tags = self._fix_tags_list(filter_tags)

        for x in self.api.catalog():
            if (self.namespace and not x.startswith(self.namespace)) \
                    or (filter_repos and x not in filter_repos):
                continue
            if filter_tags:
                for y in self.api.tags(x):
                    if filter_tags != '*' and y not in filter_tags:
                        continue
                    yield Image('{}:{}'.format(x, y))
            else:
                yield Image(x)


class TagCommand(RegistryCommand):
    """
    Administra los `tags` para el despliegue de los servicios.

    Usage: tag COMMAND [ARGS...]

    Comandos disponibles:
        ls        Lista los `tags` diponibles en el `repositorio`.
        add       Crea un nuevo `tag` a partir de otro existente.
        delete    Elimina un `tag` existente.
    """
    def ls(self, **kwargs):
        """
        Lista los `tags` existentes en el repositorio.

        Usage: ls [options] [IMAGE...]

        Opciones:
            -t tags, --filter-tags=tags     Lista de `tags` separados por comas,
                                            ex: "dev,rc,latest" [default: *]
        """
        import json, pprint
        for image in self._list(kwargs['image'], kwargs['--filter-tags']):
            print(image)
            if self.verbose:
                manifest = self.api.fat_manifest(image.repository, image.tag)
                pprint.pprint(json.loads(manifest['history'][0]['v1Compatibility']))



    def add(self, **kwargs):
        """
        Crea un nuevo `tag` a partir de otro existente.

        Usage: add SOURCE_IMAGE_TAG TARGET_TAG
        """
        print(kwargs)

    def delete(self, **kwargs):
        """
        Elimina un `tag` existente.

        Usage: delete [options] IMAGE_TAG [IMAGE_TAG...]

        Opciones:
            -y, --yes    Responde "SI" a todas las preguntas.
        """
        print(kwargs)


class MakeCommand(RegistryCommand):
    """
    Crea las `imágenes` para los entornos de `QA/TESTING` y `PRODUCCIÓN`.

    Usage: make COMMAND [ARGS ...]

    Comandos disponibles:
        test    Crea las `imágenes` para el entorno de `QA/TESTING`.
        prod    Crea las `imágenes` para el entorno de `PRODUCCIÓN`.
    """
    def test(self, **kwargs):
        """
        Crea las `imágenes` para el entorno de `QA/TESTING`.

        Usage: test [options]

        Opciones:
            -y, --yes    Responde "SI" a todas las preguntas.
        """
        print(kwargs)

    def prod(self, **kwargs):
        """
        Crea las `imágenes` para el entorno de `PRODUCCIÓN`.

        Usage: prod [options]

        Opciones:
            -y, --yes    Responde "SI" a todas las preguntas.
        """
        print(kwargs)


# top level command
class TopLevelCommand(Command):
    """
    AySA, Utilidad para la gestión de despliegues en `docker`.

    Usage:
        aysa [options] COMMAND [ARGS...]

    Opciones:
        -h, --help                              Muestra la `ayuda` del programa.
        -v, --version                           Muestra la `versión` del programa.
        -D, --debug                             Activa el modo `debug`.
        -O filename, --debug-output=filename    Archivo de salida para el modo `debug`.
        -E filename, --env=filename             Archivo de configuración del entorno (`.ini`),
                                                el mismo será buscado en la siguiente ruta
                                                de no ser definido: `~/.aysa/config.ini`.
        -X config, --proxy=config               Configuración del `proxy` en una sola línea:
                                                `<protocol>://<username>:<password>@<host>:<port>`
        -V, --verbose                           Activa el modo `verbose`.

    Comandos disponibles:
        tag     Administra los `tags` del `repositorio`.
        make    Crea las `imágenes` para los entornos de `QA/TESTING` y `PRODUCCIÓN`.

    > Utilice `aysa COMMAND (-h|--help)` para ver la `ayuda` especifica del comando.
    """
    def __init__(self, options=None, **kwargs):
        super().__init__('aysa', options, **kwargs)

    commands = {'tag': TagCommand,'make': MakeCommand}


def main():
    try:
        TopLevelCommand({'version': __version__})()
        sys.exit(0)

    except KeyboardInterrupt:
        log.error("Aborting.")

    except NoSuchCommand:
        log.error("No such command.")

    except Exception as e:
        pass

    sys.exit(1)

# python -m aysa tag ls -v web:dev
# python -m aysa tag add web:dev rc
# python -m aysa tag delete web:dev
# python -m aysa make test
# python -m aysa make prod
# python -m aysa make prod -y
