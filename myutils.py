# pylint: disable=missing-docstring, no-self-use, line-too-long
#
# Some utility classes
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#


import os
import sys
import errno
import datetime

# Works also when running async
def writef(string):
    sys.stdout.write(string)
    sys.stdout.flush()

class Logging:
    def __init__(self, filename, debug_mode):
        self._filename = filename
        self._debug_mode = debug_mode

    def debug(self, *args):
        if self._debug_mode:
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

# Functions
# ========

def get_output_dir(folder='/output'):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = current_dir + os.path.join(folder, datetime.datetime.now().isoformat())
        os.makedirs(output_dir)
        return output_dir

    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise Exception('Error in getOutputPath!')

# histories = [[val11,...,val1n],...,[valm1,...valmn]]
# header = [header1,...,headern]
def save_csv_file(filename, histories, headers=None, output_dir=None, csv_sep=';'):
    print('ZZZZZ', filename, headers, output_dir)
    if headers:
        headers = csv_sep.join(headers)

    res = zip(*histories)

    # Save the performance history to file
    if not output_dir:
        output_dir = get_output_dir()
    output_path = os.path.join(output_dir, filename)
    fp = open(output_path, 'w')
    if headers:
        print(headers, file=fp)
    print('\n'.join([csv_sep.join([str(x).replace('.', ',')
                                         for x in line]) for line in res]), file=fp)
    fp.close()
