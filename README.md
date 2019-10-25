# AySA Docker

Marco de trabajo para el despliegue de contenedores.

## Dependencias

Las dependencias se encuentran definidas en el archivo `Pipfile`, para la gestión de las mismas es requerido tener instalado `pipenv`, visitar [**site**](https://pipenv.readthedocs.io/).

### Pipenv

* Documentación: [**usage**](https://pipenv.readthedocs.io/en/latest/#pipenv-usage).
* Instalación: `pip install pipenv`.

#### Instalación de las dependencias:

```bash
> pipenv install
```

#### Iniciar el Shell:

```bash
> pipenv shell
```

#### Crear el archivo `requirements.txt`

```bash
> pipenv lock --requirements > requirements.txt
```

## Documentación

Definir en cada archivo la siguiente cabecera:

```python
# Author: Nombre X. APELLIDO [(x0000000) optional]
# Email account at domain.com
# Created: ${YEAR}/${MONTH}/${DAY} [${HOUR}:${MINUTE} optional]
# ~

${END}
```
