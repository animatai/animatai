#!./venv3/bin/python
# pylint: disable=missing-docstring, exec-used, invalid-name
import sys

mod = sys.argv[1]
s = 'import worlds.' + mod
s += '\nworlds.' + mod + '.run()'

print('Generated python:\n'+s)

exec(s)
