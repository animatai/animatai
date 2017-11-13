# pylint: disable=missing-docstring, global-statement, invalid-name
#
# Copyright (C) 2017  Jonas Colmsjö, Claes Strannegård
#

# Imports
# =======

from itertools import chain

from gzutils.gzutils import Logging, save_csv_file


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
    def save(output_path):
        headers, histories = History.get()

        save_csv_file('history.csv', histories, headers, output_path)
        l.info('Collected history of ', len(list(zip(*histories))), 'steps')
