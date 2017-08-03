Animats
=======

Reference code for:

A General Model for Learning and Decision-Making in Artificial Animals by
Claes Strannegård, Nils Svangård, Jonas Colmsjö, David Lindström, Joscha Bach and Bas Steunebrink

Submitted to IJCAI-17 AGA workshop, Melbourne, Australia

This `dev` branch is work in progress and will contain a completely refactored version of the original code. 


Setup
=====

* First init `virtualenv` for Python3: `virtualenv -p python3 venv3` (`virutalenv` needs to be installed)
* Activate `virtualenv`: `source venv3/bin/activate`
* Install the necessary Python packages: `pip install -r requirements.txt`


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


Credits
=======

Using some classes from the [AIMA book](https://github.com/aimacode/aima-python)
