# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/18
# ~

from aysa import WILDCARD
from aysa.commands import Command
from aysa.docker.registry import Api, Image
from functools import partialmethod


class _RegistryCommand(Command):
    _registry_api = None

    @property
    def api(self):
        if self._registry_api is None:
            self._registry_api = Api(**self.env.registry)
        return self._registry_api

    @property
    def namespace(self):
        return self.env.registry.namespace

    def _fix_image_name(self, value, namespace=None):
        value = value.strip()
        namespace = namespace or self.namespace
        return '{}/{}'.format(namespace, value) \
            if not value.startswith(namespace) else value

    def _fix_images_list(self, values, namespace=None):
        values = values.split(',') if isinstance(values, str) else values or []
        return [self._fix_image_name(x.strip(), namespace) for x in values]

    def _fix_tags_list(self, values):
        if not values or values == WILDCARD:
            return WILDCARD
        return [x.strip() for x in values.split(',')]

    def _list(self, filter_repos=None, filter_tags=None, **kwargs):
        filter_repos = self._fix_images_list(filter_repos)
        filter_tags = self._fix_tags_list(filter_tags)
        for x in self.api.catalog():
            if (self.namespace and not x.startswith(self.namespace)) \
                    or (filter_repos and x not in filter_repos):
                continue
            if filter_tags:
                for y in self.api.tags(x):
                    if filter_tags != WILDCARD and y not in filter_tags:
                        continue
                    yield Image('{}:{}'.format(x, y))
            else:
                yield Image(x)


class ImageCommand(_RegistryCommand):
    """
    Administra los `tags` para el despliegue de los servicios.

    Usage: image COMMAND [ARGS...]

    Comandos disponibles:
        ls        Lista los `tags` diponibles en el `repositorio`.
        put       Crea un nuevo `tag` a partir de otro existente.
        delete    Elimina un `tag` existente.
    """

    def ls(self, **kwargs):
        """
        Lista los `tags` existentes en el repositorio.

        Usage: ls [options] [IMAGE...]

        Opciones:
            -v, --verbose                   Activa el modo `verbose`.
            -m, --manifest                  Activa el modo `manifest`, éste imprime
                                            en pantalla el contenido del manifiesto,
                                            anulando al modo `verbose`.
            -t tags, --filter-tags=tags     Lista de `tags` separados por comas,
                                            ex: "dev,rc,latest" [default: *]
        """
        verbose = kwargs.get('--verbose', False)
        manifest = kwargs.get('--manifest', False)
        self.output.head('Lista de `tags`:')
        for x in self._list(kwargs['image'], kwargs['--filter-tags']):
            self.output.bullet(x.repository, x.tag, tmpl='{}:{}')
            if verbose or manifest:
                tmpl = ' - {} = {}'
                m = self.api.fat_manifest(x.repository, x.tag, True)
                if verbose and not manifest:
                    self.output.write('created', m.created, tmpl=tmpl)
                    d = self.api.digest(x.repository, x.tag)
                    self.output.write('digest', d, tmpl=tmpl)
                elif manifest:
                    self.output.json(m.history)
            self.output.flush()

    def put(self, **kwargs):
        """
        Crea un nuevo `tag` a partir de otro existente.

        Usage: put SOURCE_IMAGE_TAG TARGET_TAG
        """
        src = Image(self._fix_image_name(kwargs['source_image_tag']))
        json = self.api.slim_manifest(src.repository, src.tag)
        self.api.put_manifest(src.repository, kwargs['target_tag'], json=json)

    def delete(self, **kwargs):
        """
        Elimina un `tag` existente.

        Usage: delete [options] IMAGE_TAG [IMAGE_TAG...]

        Opciones:
            -y, --yes    Responde "SI" a todas las preguntas.
        """
        if kwargs['--yes'] is True or self.yes():
            for x in kwargs['image_tag']:
                src = Image(self._fix_image_name(x))
                self.api.del_manifest(src.repository, src.tag)


class ReleaseCommand(_RegistryCommand):
    """
    Crea las `imágenes` para los entornos de `QA/TESTING` y `PRODUCCIÓN`.

    Usage: release COMMAND [ARGS...]

    Comandos disponibles:
        test    Crea las `imágenes` para el entorno de `QA/TESTING`.
        prod    Crea las `imágenes` para el entorno de `PRODUCCIÓN`.
    """
    def _release(self, tag, **kwargs):
        for x in self._list(kwargs['image']):
            self.output.write(x)

    def test(self, **kwargs):
        """
        Crea las `imágenes` para el entorno de `QA/TESTING`.

        Usage: test [IMAGE...]
        """
        self._release('rc', **kwargs)

    def prod(self, **kwargs):
        """
        Crea las `imágenes` para el entorno de `PRODUCCIÓN`.

        Usage: prod [IMAGE...]
        """
        self._release('latest', **kwargs)
