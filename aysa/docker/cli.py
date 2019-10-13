# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/12
# ~

import sys
from aysa.docker.command import Command, NoSuchCommand


class Dispatcher:
    def __init__(self, command, options):
        self.command = command
        self.options = options


class TopLevelCommand(Command):
    """
    > AySA Command Line: utilidad para la gestión de despliegues en `docker`.

    Usage:
      dreg [options] [COMMAND] [ARGS...]
      dreg -h|--help

    Options:
      -V, --version                 muestra la `versión` del programa.
      -D, --debug                   activa el modo `debug`.
      -O, --debug-output filename   archivo de salida para el modo `debug`.
      -E, --env filename            archivo de configuración del entorno (`.reg`).

    Commands:
      image     administra las `imágenes` del `repositorio`.
      tag       administra los `tags` del `repositorio`.
      make      crea las `imágenes` para los entorno de `QA` y `PRODUCCIÓN`.
      prune     purga la `registry`.

    --
    """
    pass


def main():
    try:
        cmd = Dispatcher(TopLevelCommand, {
            'options_first': True, 
            'version': 'v1.0'
        })
    except KeyboardInterrupt:
        log.error("Aborting.")
    except NoSuchCommand as e:
        log.error("No such command: %s", e.command)
    sys.exit(1)
