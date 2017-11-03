#!/bin/bash

# Make sure we have virtualenv configured
source venv3/bin/activate

# cleanup
rm -rf docs

# run lint to check code
pylint animatai/*.py test/*.py

# Genrate docs
#pydoc -w *.py
pycco animatai/*.py

# Run the unit tests
# Run a specific unittest manually like this:
# export PYTHONPATH=test
# python -m unittest test_XXX
python -m unittest discover test

# build package for distribution
rm -rf dist/
python setup.py sdist
