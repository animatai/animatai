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
# __env_classes: {env_class_name: [(class_name1, count1, ..., class_namen, countn)]}
#
class History:

    __history = {}
    __headers = {}
    __filenames = {}
    __env_classes = {}

    @staticmethod
    def add_dataset(dsname, dsheaders, filename=None):
        filename = filename or 'history.csv'
        History.__history[dsname] = []
        History.__headers[dsname] = dsheaders
        if filename not in History.__filenames:
            History.__filenames[filename] = []
        History.__filenames[filename].append(dsname)

    # setup classes to collect stats for in an environment
    @staticmethod
    def add_env_classes(env, env_classes, filename=None):
        History.__env_classes[env.__name__] = env_classes
        History.add_dataset(env.__name__, [env.__name__], filename)

    @staticmethod
    def add_row(dataset, values):
        if dataset not in History.__history:
            History.add_dataset(dataset, [dataset])
        History.__history[dataset].append(values)

    # implement the functions necessary to be an agent observer
    @staticmethod
    def agent_step(agent, percept, action, time):
        History.add_row(agent.__name__, (str(percept), str(action), str(time)))

    # implement the functions necessary to be an environment observer
    @staticmethod
    def env_step(env):
        res = []
        for cls in History.__env_classes[env.__name__]:
            res.extend([cls, env.calc_objects(cls)])
        History.add_row(env.__name__, tuple(res))

    @staticmethod
    def get_dataset(dataset):
        res = list(History.__headers[dataset])
        res.extend(History.__history[dataset])
        return res

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

        l.info('Collected history of ', len(list(zip(*histories))), 'steps')
