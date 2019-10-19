# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/12
# ~

import sys
import logging
from aysa import __version__
from aysa.commands import NoSuchCommand, Command
from aysa.commands.registry import ImageCommand, ReleaseCommand
from aysa.docker.registry import Registry, Api, Image, get_parts


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
        -h, --help                              Muestra la `ayuda` del programa.
        -v, --version                           Muestra la `versión` del programa.
        -D, --debug                             Activa el modo `debug`.
        -O filename, --debug-output=filename    Archivo de salida para el modo `debug`.
        -E filename, --env=filename             Archivo de configuración del entorno (`.ini`),
                                                el mismo será buscado en la siguiente ruta
                                                de no ser definido: `~/.aysa/config.ini`.
        -X config, --proxy=config               Configuración del `proxy` en una sola línea:
                                                `<protocol>://<username>:<password>@<host>:<port>`

    Comandos disponibles:
        image       Lista las `imágenes` y administra los `tags` del `repositorio`.
        release     Crea las `imágenes` para los entornos de `QA/TESTING` y `PRODUCCIÓN`.
        deploy      ...

    > Utilice `aysa COMMAND (-h|--help)` para ver la `ayuda` especifica del comando.
    """
    def __init__(self, options=None, **kwargs):
        super().__init__('aysa', options, **kwargs)

    commands = {'image': ImageCommand, 'release': ReleaseCommand,
                'deploy': None}


# dispatch
def main():
    try:
        TopLevelCommand({'version': __version__})()
        sys.exit(0)
    except KeyboardInterrupt:
        log.error("Aborting.")
    except NoSuchCommand:
        log.error("No such command.")
    except Exception as e:
        log.error(e)
    sys.exit(1)
