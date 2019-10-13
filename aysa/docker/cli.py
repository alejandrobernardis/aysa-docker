# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/12
# ~

import sys
from aysa.docker.command import NoSuchCommand


class TopLevelCommand:
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
    --
    """
    def __init__(self, command, options=None, **kwargs):
        pass
    

def main():
    try:
        pass
    except KeyboardInterrupt:
        log.error("Aborting.")
    except NoSuchCommand as e:
        log.error("No such command: %s", e.command)
    sys.exit(1)
