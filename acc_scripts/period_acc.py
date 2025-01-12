#!/usr/bin/env python3

# -*- encoding: utf-8 -*-
#
# Copyright 2020 LIP
#
# Author: Mario David <mariojmdavid@gmail.com>
#
"""Monthly resource usage for all projects
"""

import sys
import os
from datetime import datetime, timedelta
import h5py
import osacc_functions as oaf
from dateutil.relativedelta import *


if __name__ == '__main__':
    ev = oaf.get_conf()
    filename = oaf.get_hdf_filename(ev)
    infra = ev['openstack_host']
    hourdt = 3600 / ev['delta_time']

    print(80 * '=')
    print('Input hdf filename:', filename)
    # Control file for the date
    date_ctl = ev['out_dir'] + '/acc_control'
    year_ini = ev['year_ini']
    month_ini = ev['month_ini']
    day_ini = 1

    if os.path.isfile(date_ctl):
        with open(date_ctl, 'r', encoding='utf-8') as fctl:
            date_ini = fctl.read()
            (y_ini, m_ini, d_ini) = date_ini.split('-')
            year_ini = int(y_ini)
            month_ini = int(m_ini)
            day_ini = int(d_ini)
            print(f'Last accounting date: {date_ini}')

    date_ini = datetime(year_ini, month_ini, day_ini, 0, 0, 0)
    last_day = datetime.now()-timedelta(1)
    date_end = datetime(last_day.year, last_day.month, last_day.day, 23, 59, 59)
    day_ini = date_ini
    str_date = ''
    with h5py.File(filename, 'r') as f:
        while (day_ini <= date_end):
            str_year = str(day_ini.year)
            str_month = '{:02d}'.format(day_ini.month)
            str_day = '{:02d}'.format(day_ini.day)
            str_date = str_year + '-' + str_month + '-' + str_day
            fname = ev['out_dir'] + '/' + 'cloud-' + str_date + '.csv'
            day_end = datetime(day_ini.year, day_ini.month, day_ini.day, 23, 59, 59)
            ti = oaf.to_secepoc(day_ini)
            tf = oaf.to_secepoc(day_end)
            ts = f['date'][:]
            idx_start = oaf.time2index(ev, ti, ts)
            idx_end = oaf.time2index(ev, tf, ts)

            print(80*'+')
            print(f'Date: {day_ini} -> {day_end}')
            print(f'Date epoc: {ti} -> {tf}')
            print(f'HDF5 date index: {idx_start} -> {idx_end}')
            with open(fname, 'w') as fout:
                hdrline = 'project'
                for mtr in oaf.METRICS:
                    hdrline = hdrline + ',' + mtr + '*hour'

                fout.write(hdrline + '\n')
                for group in f:
                    if group == "date":
                        continue

                    csvline = group
                    dgroup = f[group]
                    for mtr in oaf.METRICS:
                        summtr = 0
                        for i in range(idx_start, idx_end):
                            data = dgroup[mtr]
                            summtr = summtr + (data[i]/hourdt)

                        csvline = csvline + ',' + str(summtr)

                    fout.write(csvline + '\n')

            day_ini = day_end

    with open(date_ctl, 'w', encoding='utf-8') as fctl:
        fctl.write(str_date)
