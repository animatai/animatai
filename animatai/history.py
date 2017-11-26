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
l = Logging('history', DEBUG_MODE)


# The code
# =========

#
# A singleton collecting history that can be saved to a CSV file
#
# __history: {dataset: [(col1, ..., coln)]} - dict list with tuples (or lists)
# __headers: {dataset: [header1, ..., headern]} - dict with column headers
# __filenames: {filename: [dataset1, ..., datasetn]} - dict mapping datasets to filenaames
#
class History:

    __history = {}
    __headers = {}
    __filenames = {}

    @staticmethod
    def add_dataset(dsname, dsheaders, filename=None):
        filename = filename or 'history.csv'
        History.__history[dsname] = []
        History.__headers[dsname] = dsheaders
        if filename not in History.__filenames:
            History.__filenames[filename] = []
        History.__filenames[filename].append(dsname)

    @staticmethod
    def add_row(dataset, values):
        if dataset not in History.__history:
            History.add_dataset(dataset, [dataset])
        History.__history[dataset].append(values)

    # implement the functions necessary to be an observer
    @staticmethod
    def agent_step(agent, percept, action, time):
        History.add_row(agent.__name__, (str(percept), str(action), str(time)))

    @staticmethod
    def get(filename=None):
        filename = filename or 'history.csv'

        headers = []
        histories = []
        for dataset, history in History.__history.items():
            if dataset in History.__filenames[filename]:
                headers.extend(History.__headers[dataset])
                histories.append(history)

        histories = list(zip(*histories))
        histories = list(map(list, map(chain.from_iterable, histories)))
        return (headers, histories)

    @staticmethod
    def save(filename=None, output_dir=None, csv_sep=';'):
        filename = filename or 'history.csv'
        output_dir = output_dir or get_output_dir('/../output', __file__)

        output_path = os.path.join(output_dir, filename)

        headers, histories = History.get(filename)
        headers = csv_sep.join(headers)

        filep = open(output_path, 'w')
        print(headers, file=filep)
        print('\n'.join([csv_sep.join([str(x).replace('.', ',')
                                       for x in line]) for line in histories]),
              file=filep)
        filep.close()

        #save_csv_file('history.csv', histories, headers, output_dir)
        l.info('Collected history of ', len(list(zip(*histories))), 'steps')
