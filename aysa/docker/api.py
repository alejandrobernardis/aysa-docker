# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/15
# ~

import re
import requests
from requests.auth import HTTPBasicAuth

# {registry:port}/{namespace}/{repository}:{tag}
TAG_SEP = ':'
REPO_SEP = '/'

rx_registry = re.compile(r'\w+((\.\w+)+)?(?::\d{1,5})?\/', re.I)


def remove_registry(value):
    registry = get_registry(value)
    if registry is not None:
        value = value.replace(registry, '')
    return value


def get_tag(value):
    return remove_registry(value).rsplit(TAG_SEP, 1)[-1]


def get_repository(value):
    return remove_registry(value).rsplit(TAG_SEP, 1)[0]


def get_namespace(value):
    value = get_repository(value)
    if REPO_SEP not in value:
        return None
    return value.rsplit(REPO_SEP, 1)[0]


def get_image(value):
    return get_repository(value).rsplit(REPO_SEP, 1)[-1]


def get_registry(value):
    r = rx_registry.match(value)
    if r is not None:
        return r.group()
    return None


def get_parts(value):
    return {
        'registry': get_registry(value),
        'repository': get_repository(value),
        'namespace': get_namespace(value),
        'image': get_image(value),
        'tag': get_tag(value),
    }


def scheme(endpoint):
  if re.match(r'(localhost|.*\.local(?:host)?(?::\d{1,5})?)$', endpoint):
    return 'http'
  else:
    return 'https'


class Registry:
    """
    Registry Client (simple)
    """
    def __init__(self, host, insecure=False, verify=True, credentials=None):
        self.host = host
        self.insecure = insecure
        self.verify = verify if insecure is False else True
        self.scheme = scheme(host) if insecure is False else 'http'
        self.credentials = credentials

    def get_baseurl(self):
        return '{}://{}/v2'.format(self.scheme, self.host)

    def get_credentials(self, split=False):
        if split is True:
            return self.credentials.split(':')
        return self.credentials

    def session(self, headers=None, timeout=10):
        s = requests.Session()
        if self.credentials is not None:
            s.auth = HTTPBasicAuth(*self.get_credentials(True))
        s.headers.update(headers or {})
        s.headers['Accept'] = 'application/vnd.docker.distribution.manifest' \
                              '.v2+json'
        s.verify = self.verify
        s.timeout = timeout
        return s

    def request(self, method, *args, **kwargs):
        headers = kwargs.pop('headers', None)
        with self.session(headers) as req:
            response = req.request(method, *args, **kwargs)
            try:
                response.raise_for_status()
            except requests.HTTPError:
                data = response.json()
                if 'errors' in data:
                    error = data['errors'][0]
                    raise RegistryError('{code}: {message}'.format(**error))
            return response


class Entity:
    url = None
    url_template = None
    methods_supported = None

    def __init__(self, client):
        self.client = client

    def set_url(self, **kwargs):
        if self.url_template is None:
            raise RegistryError('Método no soportado para la entidad: "{}".'
                                .format(self.__class__.__name__))
        self.url = self.url_template.format(**kwargs)

    def request(self, method, *args, jsonr=False, **kwargs):
        method = method.upper()
        if self.methods_supported and method not in self.methods_supported:
            raise RegistryError('Método "{}" no soportado para "{}".'
                                .format(method, self.url))
        url = self.client.get_baseurl() + self.url
        response = self.client.request(method, url, *args, **kwargs)
        return response if jsonr is False else response.json()


class IterEntity(Entity):
    response_key = None
    response_data = None

    def __init__(self, client, prefix_filter=None):
        self.client = client
        self.prefix_filter = prefix_filter

    def get(self, *args, **kwargs):
        response_data = self.request('GET', *args, **kwargs).json()
        if self.response_key not in response_data:
            raise RegistryError('La clave "{}" no se encuentra dentro de la '
                                'rspuesta.'.format(self.response_key))
        self.response_data = response_data[self.response_key]

    def __iter__(self):
        # TODO(i0608156): Evaluar la implementación de un paginador.

        if self.response_data is None:
            self.get()

        for item in self.response_data:
            if self.prefix_filter and not item.startswith(self.prefix_filter):
                continue
            yield item


class Catalog(IterEntity):
    url = '/_catalog'
    methods_supported = 'GET'
    response_key = 'repositories'


class Tags(IterEntity):
    url_template = '/{name}/tags/list'
    methods_supported = 'GET'
    response_key = 'tags'

    def __init__(self, client, name):
        super().__init__(client)
        self.set_url(name=name)


class Manifest(Entity):
    url_template = '/{name}/manifests/{reference}'
    methods_supported = 'GET,PUT,DELETE'

    def __init__(self, client, name, reference):
        super().__init__(client)
        self.set_url(name=name, reference=reference)


class Api:
    """
    opt = dict(insecure=True, credentials='dashboard:dashboard')
    api = Api('10.17.65.128:5000', **opt)

    for x in api.catalog():
        for y in api.tags(x):
            print(x, y)
    """
    def __init__(self, host, insecure=False, verify=True, credentials=None):
        self.registry = Registry(host, insecure, verify, credentials)

    def catalog(self):
        return Catalog(self.registry)

    def tags(self, name):
        return Tags(self.registry, name)

    def manifest(self, name, reference):
        return Manifest(self.registry, name, reference)

    def digest(self, name, reference):
        response = self.manifest(name, reference).request('GET')
        return response.headers.get('Docker-Content-Digest', None)

    def get_manifest(self, name, reference):
        return self.manifest(name, reference).request('GET')

    def put_manifest(self, name, reference):
        return self.manifest(name, reference).request('PUT')

    def delete_manifest(self, name, reference):
        return self.manifest(name, reference).request('DELETE')


class RegistryError(Exception):
    pass
