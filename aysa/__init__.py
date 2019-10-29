# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/12
# ~

import os

try:
    import ujson as json
    is_ujson = True

except ImportError:
    import json
    is_ujson = False


__all__ = [
    '__title__',
    '__summary__',
    '__uri__',
    '__version__',
    '__author__',
    '__email__',
    '__license__',
    '__copyright__',
    'json',
    'WIN',
    'EMPTY',
    'SEGMENT',
    'VERSION'
]

# const
WIN = os.name == 'nt'
EMPTY = object()
WILDCARD = '*'

# version
SEGMENT = 'dev'
VERSION = (1, 0, 0, SEGMENT, 1)

# doc
__title__ = 'aysa-docker'
__summary__ = 'Marco de trabajo para el despliegue de contenedores.'
__uri__ = 'https://github.com/alejandrobernardis/aysa-docker/'
__issues__ = 'https://github.com/alejandrobernardis/aysa-docker/issues/'
__version__ = '.'.join([str(x) for x in VERSION])
__author__ = 'Alejandro M. BERNARDIS and individual contributors.'
__email__ = 'alejandro.bernardis@gmail.com'
__license__ = 'MTI License, Version 2.0'
__copyright__ = 'Copyright 2019 {}'.format(__author__)
