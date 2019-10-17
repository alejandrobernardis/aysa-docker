```python
import configparser
parser = configparser.RawConfigParser()
parser._interpolation = configparser.ExtendedInterpolation()
parser.read('home/user/.aysa/endpoints')

for x in parser.sections():
    print('\n[%s]' % x)
    for y, z in parser[x].items():
        print(y, '=', z)
```