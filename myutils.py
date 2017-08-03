# pylint: disable=missing-docstring, no-self-use, line-too-long
#
# Some utility classes
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#

class Logging:
    def __init__(self, filename, debug_mode):
        self._filename = filename
        self._debug_mode = debug_mode

    def debug(self, *args):
        if self._filename:
            print('DEBUG:'+self._filename+':', *args)

    def error(self, *args):
        print('ERROR::', *args)

    def warn(self, *args):
        print('WARNING:'+self._filename+':', *args)

    def info(self, *args):
        print('INFO:'+self._filename+':', *args)

# dot.notation access to dictionary attributes
# from https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary/23689767#23689767
class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
