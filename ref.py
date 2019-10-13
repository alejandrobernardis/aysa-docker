CONST_COMMAND = 'COMMAND'
CONST_SERVICE = 'SERVICE'
CONST_ARGS = 'ARGS'

log = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stderr)


def docopt_helper(docstring, *args, **kwargs):
    try:
        return docopt(docstring, *args, **kwargs)
    except DocoptExit:
        raise SystemExit(docstring)


def get_handler(command, command_name):
    command_name = command_name.replace('-', '_')

    if not hasattr(command, command_name):
        raise NoSuchCommand(command_name, command)
    
    return getattr(command, command_name)


class Dispatcher:
    def __init__(self, command, options):
        self.command = command
        self.command_help = getdoc(command)
        self.options = options

    def parse(self, argv):
        options = docopt_helper(self.command_help, argv, **self.options)
        command = options[CONST_COMMAND]

        if command is None:
            raise SystemExit(self.command_help)

        handler = get_handler(self.command, command)
        handler_help = getdoc(handler)

        if handler_help is None:
            raise SystemExit(command, self)

        handler_options = \
            docopt_helper(handler_help, options[CONST_ARGS], options_first=True)
        return options, handler, handler_options


class TopLevelCommand:
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
    def __init__(self, name, options=None):
        self.name = name
        self.options = options or {}

    def tag(self, opts):
        pass

    def find_command(self, command, *args, **kwargs):
        pass


class NoSuchCommand(Exception):
    def __init__(self, command, supercommand):
        super(NoSuchCommand, self).__init__("No such command: %s" % command)
        self.command = command
        self.supercommand = supercommand


def dispatch():
    command = Dispatcher(TopLevelCommand, {
        'options_first': True,  
        'version': __version__
    })
    return partial(perform_command, *command.parse(sys.argv[1:]))


def perform_command(options, handler, handler_options):
    if options[CONST_COMMAND] in ('help', 'version'):
        handler(handler_options)
        return

    command = TopLevelCommand(None, options=options)
    handler(command, handler_options)
