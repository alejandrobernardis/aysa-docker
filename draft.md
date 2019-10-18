```python
from configparser import ConfigParser, ExtendedInterpolation
parser = ConfigParser(interpolation=ExtendedInterpolation())
parser.read('home/user/.aysa/endpoints')

for x in parser.sections():
    print('\n[%s]' % x)
    for y, z in parser[x].items():
        print(y, '=', z)
```

```python
def tag(self, options):
    """
    Administra los `tags` para el despliegue de los servicios.

    Usage: tag COMMAND [ARGS ...]

    Comandos disponibles:
        ls        Lista los `tags` diponibles en el `repositorio`.
        add       Crea un nuevo `tag` a partir de otro existente.
        delete    Elimina un `tag` existente.

    """
    TagCommand('tag', options, parent=self).execute(**options)

def make(self, options):
    """
    Crea las `imágenes` para los entornos de `QA/TESTING` y `PRODUCCIÓN`.

    Usage:  make COMMAND [ARGS ...]

    Comandos disponibles:
        test    Crea las `imágenes` para el entorno de `QA/TESTING`.
        prod    Crea las `imágenes` para el entorno de `PRODUCCIÓN`.
    """
    MakeCommand('make', options, parent=self).execute(**options)


if verbose:
    manifest = self.api.fat_manifest(image.repository, image.tag)
    pprint.pprint(json.loads(manifest['history'][0]['v1Compatibility']))
```



