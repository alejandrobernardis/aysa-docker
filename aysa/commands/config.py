# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/21
# ~

from getpass import getpass
from aysa.commands import Command

CREDENTIALS = 'credentials'

class ConfigCommand(Command):
    """
    Lista y administra los valores de la configuración del entorno de trabajo
    definido por el archivo `~/.aysa/config.ini`.

    Usage: config COMMAND [ARGS...]

    Comandos disponibles:
        ls        Lista todas las `variables` de configuración.
        update    Actualiza el valor de una nueva `variable` de configuración.
                  Para la variable `registry.credentials` NO es necesario
                  pasar el valor de la contraseña, éste es solicitado
                  posteriomente.
    """
    def ls(self, **kwargs):
        """
        Lista todas las `variables` de configuración.

        Usage: ls [SECTION...]
        """
        sections_filter = kwargs['section']
        self.output.blank()
        for s, sv in self.env.items():
            if sections_filter and s not in sections_filter:
                continue
            self.output.write(s, tmpl='[{}]:', upper=True)
            for k, v in sv.items():
                if k == CREDENTIALS and v:
                    v = '{}:******'.format(v.split(':')[0])
                self.output.write(k, v, tmpl='{} = "{}"', tab=2)
            self.output.blank()

    def update(self, **kwargs):
        """
        Actualiza el valor de una nueva `variable` de configuración.
        Para la variable `registry.credentials` NO es necesario pasar
        el valor de la contraseña, éste es solicitado posteriomente.

        Usage: update SECTION_VARIABLE VALUE
        """
        section, _, variable = kwargs['section_variable'].partition('.')
        try:
            if variable not in self.env[section]:
                raise KeyError('La sección y/o variable "{}.{}" no están '
                               'soportadas por la acutal versión del '
                               'archivo de configuración.'
                               .format(section, variable))
            new_value = kwargs['value']
            if variable == CREDENTIALS:
                password = getpass()
                new_value = '{}:{}'.format(new_value, password)
            self.env[section][variable] = new_value
            self.env_save()
        except:
            pass
