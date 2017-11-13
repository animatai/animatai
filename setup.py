# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='animatai',
    version='0.1.1',
    description='Ecosystem with animats for development of Artificial General Intelligence',
    long_description=long_description,
    url='https://github.com/animatai/animatai',
    author='Jonas Colmsjö',
    author_email='jonas.colmsjo@gizur.com',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='animat ai agi artificial intelligence',
    packages=find_packages(exclude=['contrib', 'docs', 'test']),
    install_requires=['asyncio', 'numpy', 'gzutils', 'websockets'],
    extras_require={
        'dev': ['Pycco', 'pylint'],
        'test': ['coverage'],
    },
   package_data={
      '': ['LICENSE', 'index.html', 'images/*', 'config.py.template', 'start.sh'],
   },
)
