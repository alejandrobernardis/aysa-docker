# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/12
# ~

import sys
import logging
from aysa import __version__
from aysa.commands import Command
from aysa.commands.config import ConfigCommand
from aysa.commands.registry import RegistryCommand, ReleaseCommand
from aysa.commands.remote import RemoteCommand


# cli logger
log = logging.getLogger(__name__)


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
        -V, --verbose                           Activa el modo `verbose`.
        -O filename, --debug-output=filename    Archivo de salida para el modo `debug`.
        -E filename, --env=filename             Archivo de configuración del entorno (`.ini`),
                                                el mismo será buscado en la siguiente ruta
                                                de no ser definido: `~/.aysa/config.ini`.
        -X url, --proxy=url                     Configuración del `proxy` en una sola línea:
                                                `<protocol>://<username>:<password>@<host>:<port>`

    Comandos disponibles:
        config      Lista y administra los valores de la configuración del entorno de trabajo
                    definido por el archivo `~/.aysa/config.ini`
        registry    Lista las `imágenes` y administra los `tags` del `repositorio`.
        release     Crea las `imágenes` para los entornos de `QA/TESTING` y `PRODUCCIÓN`.
        remote      Despliega las `imágenes` en los entornos de `DESARROLLO` y `QA/TESTING`.

    > Utilice `aysa COMMAND (-h|--help)` para ver la `ayuda` especifica del comando.
    """

    def __init__(self, options=None, **kwargs):
        super().__init__('aysa', options, **kwargs)

    commands = {
        'config': ConfigCommand,
        'registry': RegistryCommand,
        'release': ReleaseCommand,
        'remote': RemoteCommand,
    }


# dispatcher
def main():
    try:
        TopLevelCommand({'version': __version__}).parse()
    except KeyboardInterrupt:
        log.error("Aborting.")
    except Exception as e:
        log.error(e)
    sys.exit(1)
