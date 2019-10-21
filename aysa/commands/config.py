# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/21
# ~

from aysa.commands import Command


class ConfigCommand(Command):
    """
    Lista y administra los valores de la configuración del entorno de trabajo
    definido por el archivo `~/.aysa/config.ini`

    Usage: config COMMAND [ARGS...]

    Comandos disponibles:
        ls      ...
        add     ...
        rm      ...

    """
