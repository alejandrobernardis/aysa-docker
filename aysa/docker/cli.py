# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/12
# ~

import sys
from aysa.docker.command import Command, NoSuchCommand


class TopLevelCommand(Command):
    """
    > AySA Command Line: utilidad para la gestión de despliegues en `docker`.

    Usage:
        aysa [options] [COMMAND] [ARGS...]
        aysa -h|--help

    Options:
        -V, --version                 Muestra la `versión` del programa.
        -D, --debug                   Activa el modo `debug`.
        -O, --debug-output filename   Archivo de salida para el modo `debug`.
        -E, --env filename            Archivo de configuración del entorno (`.reg`).

    Commands:
        resume    Información respecto del estado del `repositorio`.
        tag       Administra los `tags` del `repositorio`.
        make      Crea las `imágenes` para los entorno de `QA` y `PRODUCCIÓN`.
        prune     Purga la `repositorio`.

    --
    """
    def __init__(self, command, options=None, **kwargs):
        super().__init__(None, options, **kwargs)
    
    def resume(self, options):
        pass

    def tag(self, options):
        pass

    def make(self, options):
        pass

    def prune(self, options):
        pass


def main():
    try:
        pass
    except KeyboardInterrupt:
        log.error("Aborting.")
    except NoSuchCommand as e:
        log.error("No such command: %s", e.command)
    sys.exit(1)
