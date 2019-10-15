# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/12
# ~
# -V, --verbose     Activa el modo `verbose`.

import sys
import aysa
import logging
from aysa.docker.command import NoSuchCommand, Command

# logger
log = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stderr)


# top level command
class TopLevelCommand(Command):
    """
    AySA, Utilidad para la gestión de despliegues en `docker`.
    
    Usage:
        aysa [options] COMMAND [ARGS...]

    Options:
        -h, --help                    Muestra la `ayuda` del programa.
        -V, --version                 Muestra la `versión` del programa.
        -D, --debug                   Activa el modo `debug`.
        -O, --debug-output=filename   Archivo de salida para el modo `debug`.
        -E, --env=filename            Archivo de configuración del entorno (`.reg`).
        -X, --proxy config            Configuración del `proxy` en una sola línea:
                                      `<protocol>://<username>:<password>@<host>:<port>`

    Available commands:
        tag         Administra los `tags` del `repositorio`.
        make        Crea las `imágenes` para los entornos de `QA/TESTING` y `PRODUCCIÓN`.
    """
    def __init__(self, options=None, **kwargs):
        super().__init__(None, options, **kwargs)

    def tag(self):
        """
        * TAG: Administra los `tags` para el despliegue de los servicios.

        Usage:
            tag COMMAND [ARGS ...]
        
        Available commands:
            ls          Lista los `tags` diponibles en el `repositorio`.
            add         Crea un nuevo `tag` a partir de otro existente.
            delete      Elimina un `tag` existente.
        """
        pass

    def make(self):
        """
        * MAKE: Crea las `imágenes` para los entornos de `QA/TESTING` y `PRODUCCIÓN`.

        Usage:
            make COMMAND [ARGS ...]
        
        Available commands:
            test    Crea las `imágenes` para el entorno de `QA/TESTING`.
            prod    Crea las `imágenes` para el entorno de `PRODUCCIÓN`.
        """
        pass


def main():
    try:
        cmd = TopLevelCommand({'version': aysa.__version__})
        cmd.parse()
    except KeyboardInterrupt:
        log.error("Aborting.")
    except NoSuchCommand:
        log.error("No such command.")
    sys.exit(1)
