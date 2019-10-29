# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/29
# ~

import os
import pip


def main():
    os.system('python -m pip install {}'.format(
        'https://github.com/alejandrobernardis/aysa-docker/archive'\
        '/master.zip'
    ))


if __name__ == '__main__':
    main()
