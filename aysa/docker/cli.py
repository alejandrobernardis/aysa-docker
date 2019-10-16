# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/12
# ~
# -V, --verbose     Activa el modo `verbose`.

import sys
import logging
from aysa import __version__
from aysa.docker.api import Registry
from aysa.docker.cmd import NoSuchCommand, Command

# logger
log = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stderr)


# top level command
class TopLevelCommand(Command):
    """
    AySA, Utilidad para la gestión de despliegues en `docker`.

    Usage:
        aysa [options] COMMAND [ARGS...]

    Opciones:
        -h, --help                    Muestra la `ayuda` del programa.
        -v, --version                 Muestra la `versión` del programa.
        -D, --debug                   Activa el modo `debug`.
        -O, --debug-output=filename   Archivo de salida para el modo `debug`.
        -E, --env=filename            Archivo de configuración del entorno (`.reg`).
        -X, --proxy config            Configuración del `proxy` en una sola línea:
                                      `<protocol>://<username>:<password>@<host>:<port>`
        -V, --verbose                 Activa el modo `verbose`.

    Comandos disponibles:
        tag         Administra los `tags` del `repositorio`.
        make        Crea las `imágenes` para los entornos de `QA/TESTING` y `PRODUCCIÓN`.

    * Utilice `aysa COMMAND (-h|--help)` para ver la `ayuda` especifica del comando.
    """
    def __init__(self, options=None, **kwargs):
        super().__init__(None, options, **kwargs)

    def tag(self, **kwargs):
        """
        Administra los `tags` para el despliegue de los servicios.

        Usage:
            tag COMMAND [ARGS ...]

        Comandos disponibles:
            ls          Lista los `tags` diponibles en el `repositorio`.
            add         Crea un nuevo `tag` a partir de otro existente.
            delete      Elimina un `tag` existente.

        """
        TagCommand(kwargs, parent=self).execute(**kwargs)

    def make(self, **kwargs):
        """
        Crea las `imágenes` para los entornos de `QA/TESTING` y `PRODUCCIÓN`.

        Usage:
            make COMMAND [ARGS ...]

        Comandos disponibles:
            test    Crea las `imágenes` para el entorno de `QA/TESTING`.
            prod    Crea las `imágenes` para el entorno de `PRODUCCIÓN`.
        """
        MakeCommand(kwargs, parent=self).execute(**kwargs)


class TagCommand(Command):
    def __init__(self, options=None, **kwargs):
        super().__init__(self.__class__.__name__, options, **kwargs)

    def ls(self, **kwargs):
        """
        Lista los `tags` existentes en el repositorio.

        Usage:
            ls [options] [IMAGE...]
        """
        print(kwargs)

    def add(self, **kwargs):
        """
        Crea un nuevo `tag` a partir de otro existente.

        Usage:
            add SOURCE_IMAGE_TAG TARGET_TAG
        """
        print(kwargs)

    def delete(self, **kwargs):
        """
        Elimina un `tag` existente.

        Usage:
            delete [options] IMAGE_TAG [IMAGE_TAG...]

        Opciones:
            -y, --yes       Responde "SI" a todas las preguntas.
        """
        print(kwargs)


class MakeCommand(Command):
    def test(self, **kwargs):
        """
        Crea las `imágenes` para el entorno de `QA/TESTING`.

        Usage:
            test [options]

        Opciones:
            -y, --yes       Responde "SI" a todas las preguntas.
        """
        print(kwargs)

    def prod(self, **kwargs):
        """
        Crea las `imágenes` para el entorno de `PRODUCCIÓN`.

        Usage:
            prod [options]

        Opciones:
            -y, --yes       Responde "SI" a todas las preguntas.
        """
        print(kwargs)


def main():
    try:
        cmd = TopLevelCommand({'version': __version__})
        cmd()
    except KeyboardInterrupt:
        log.error("Aborting.")
    except NoSuchCommand:
        log.error("No such command.")
    sys.exit(1)

# python -m aysa tag ls -v web:dev
# python -m aysa tag add web:dev rc
# python -m aysa tag delete web:dev
# python -m aysa make test
# python -m aysa make prod
# python -m aysa make prod -y
