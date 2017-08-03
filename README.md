Adding support for non spatial percepts, like sound, to the environment.


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


Development
===========

Use [Google Style Guide](https://google.github.io/styleguide/pyguide.html)
and make sure that the unit tests are maintained.

Build (lint and run unit tests) with: `./build.sh`


Credits
=======

Using some classes from the [AIMA book](https://github.com/aimacode/aima-python)
