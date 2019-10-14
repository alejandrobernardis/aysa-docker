# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/12
# ~

import sys
import aysa
from aysa.docker.command import NoSuchCommand, Command


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
        -X, --proxy config            Configuración del `proxy` en una sola línea:
                                      `<protocol>://<username>:<password>@<host>:<port>`

    Available commands:
        resume          Muestra el `estado` de los servicios deplegados.
        registry        Administra los `repositorios` de imágenes.
        container       Administra los `contenedores` de los escenarios disponibles.
    """
    def __init__(self, command, options=None, **kwargs):
        super().__init__(command, options, **kwargs)
    

def main():
    try:
        cmd = TopLevelCommand(None, {'version': aysa.__version__})
        result = cmd(sys.argv[1:])
        return 

    except KeyboardInterrupt:
        pass

    except NoSuchCommand as e:
        pass

    sys.exit(1)
