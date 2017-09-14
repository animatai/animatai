Animats
=======

Reference code for:

A General Model for Learning and Decision-Making in Artificial Animals by
Claes Strannegård, Nils Svangård, Jonas Colmsjö, David Lindström, Joscha Bach and Bas Steunebrink

Submitted to IJCAI-17 AGA workshop, Melbourne, Australia

This `dev` branch is work in progress and will contain a completely refactored
version of the original code.


Setup
=====

At least Python 3.5 is needed since `async` is used in `wsserver.py`. I'm using Python 3.6 here.

* First init `virtualenv` for Python3: `virtualenv -p python3.6 venv3` (`virutalenv` needs to be installed)
* Activate `virtualenv`: `source venv3/bin/activate`
* Install the necessary Python packages: `pip install -r requirements.txt`. Add `--no-compile` when running on ubuntu.


Run the program
==============

* Create `config.py`. Start with copying `config.py.template` and try some of the examples in there.
* Activate `virtualenv`: `source venv3/bin/activate`
* Run the server: `python wsserver.py`
* Run `index.html` in a browser and follow the instructions.
* It is possible to run a world without the web server like this: `python run_world.py blind_dog`


Development
===========

Use [Google Style Guide](https://google.github.io/styleguide/pyguide.html)
and make sure that the unit tests are maintained.

Build (lint and run unit tests) with: `./build.sh`

Create a source distribution: `python setup.py sdist`

Upload the build to the public package repo for installation with `pip`:
`twine upload dist/animats-X.Y.Z.tar.gz`


Credits
=======

Using some classes from the [AIMA book](https://github.com/aimacode/aima-python)
