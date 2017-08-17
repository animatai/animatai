#!./venv3/bin/python
# pylint: disable=missing-docstring, exec-used, invalid-name
import sys

mod = sys.argv[1]
num = sys.argv[2] or 10
s = 'import worlds.' + mod
s += '\nworlds.' + mod + '.run(None, ' + num + ')'

print('Generated python:\n'+s)

exec(s)
