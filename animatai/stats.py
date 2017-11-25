# pylint: disable=missing-docstring, global-statement, invalid-name
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#

# Imports
# =======

import os
from itertools import chain

from gzutils.gzutils import Logging, get_output_dir, save_csv_file


# Setup logging
# =============

DEBUG_MODE = True
l = Logging('stats', DEBUG_MODE)


# The code
# =========

#
# A singleton collecting history that can be saved to a CSV file
#
# __history: [(col1, ..., coln)] - list with tuples (or lists)
#
class History:

    __history = {}
    __headers = {}

    @staticmethod
    def add_dataset(name, headers):
        History.__history[name] = []
        History.__headers[name] = headers

    @staticmethod
    def add_row(dataset, values):
        History.__history[dataset].append(values)

    @staticmethod
    def get():
        headers = []
        histories = []
        for dataset, history in History.__history.items():
            headers.extend(History.__headers[dataset])
            histories.append(history)

        histories = list(zip(*histories))
        histories = list(map(list, map(chain.from_iterable, histories)))
        return (headers, histories)

    @staticmethod
    def save(output_dir=None, csv_sep=';'):
        headers, histories = History.get()
        headers = csv_sep.join(headers)

        # Save the performance history to file
        if not output_dir:
            output_dir = get_output_dir('/../output', __file__)
        output_path = os.path.join(output_dir, 'history.csv')

        filep = open(output_path, 'w')
        print(headers, file=filep)
        print('\n'.join([csv_sep.join([str(x).replace('.', ',')
                                       for x in line]) for line in histories]),
              file=filep)
        filep.close()

        #save_csv_file('history.csv', histories, headers, output_dir)
        l.info('Collected history of ', len(list(zip(*histories))), 'steps')
