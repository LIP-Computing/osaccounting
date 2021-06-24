#!/usr/bin/env python3

# -*- encoding: utf-8 -*-
#
# Copyright 2020 LIP
#
# Author: Mario David <mariojmdavid@gmail.com>
#
"""Process Monthly resource usage for all projects
"""

import csv
from tabulate import tabulate


if __name__ == '__main__':
    base_fname = 'cloud-monthly-'
    ext_fname = '.csv'
    # month_year = ['2019-05', '2019-06', '2019-07', '2019-08', '2019-09',
    #               '2019-10', '2019-11', '2019-12', '2020-01', '2020-02',
    #               '2020-03', '2020-04', '2020-05', '2020-06', '2020-07',
    #               '2020-08', '2020-09', '2020-10', '2020-11', '2020-12',
    #               '2021-01', '2021-02', '2021-03', '2021-04', '2021-05']

    month_year = ['2019-05', '2019-06', '2019-07', '2019-08', '2019-09',
                  '2019-10', '2019-11', '2019-12', '2020-01', '2020-02',
                  '2020-03', '2020-04', '2020-05', '2020-06', '2020-07',
                  '2020-08', '2020-09', '2020-10']

    p_row = list()      # List with all projects is part of the first row
    for my in month_year:
        fname = base_fname + my + ext_fname
        with open(fname, 'r') as csvin:
            reader = csv.DictReader(csvin)
            for row in reader:
                if row['project'] not in p_row:
                    p_row.append(row['project'])

    # VCPU*hour
    first_raw = ['Month_Year'] + sorted(p_row)
    all_rows_vcpus = [p_row]
    for my in month_year:
        n_row = [my]
        fname = base_fname + my + ext_fname
        with open(fname, 'r') as csvin:
            reader = csv.DictReader(csvin)
            for row in reader:
                n_row.append(row['vcpus*hour'])

        all_rows_vcpus.append(n_row)

    print(tabulate(all_rows_vcpus, headers='firstrow', tablefmt='fancy_grid'))

    # Storage TB*month
    all_rows_stor = [p_row]
    for my in month_year:
        n_row = [my]
        fname = base_fname + my + ext_fname
        with open(fname, 'r') as csvin:
            reader = csv.DictReader(csvin)
            for row in reader:
                stor_tbmonth = row['volume_gb*hour']
                n_row.append(row['volume_gb*hour'])

        all_rows_stor.append(n_row)

    print(tabulate(all_rows_stor, headers='firstrow', tablefmt='fancy_grid'))


