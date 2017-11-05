#!/bin/bash

# Make sure we have virtualenv configured
source venv3/bin/activate

# run lint to check code
pylint animatai/*.py test/*.py

# Genrate docs
#pydoc -w *.py
rm -rf doc
pycco -i -d doc animatai/*.py

# Copy project website from to the folder used by GitHub Pages
rm -rf docs
cd docsrc; make html; cd ..
cp -r docsrc/build/html docs
touch ./docs/.nojekyll

# Run the unit tests
# Run a specific unittest manually like this:
# export PYTHONPATH=test
# python -m unittest test_XXX
python -m unittest discover test

# build package for distribution
rm -rf dist/
python setup.py sdist
