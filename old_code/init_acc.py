#!/usr/bin/env python3

# -*- encoding: utf-8 -*-
#
# Copyright 2017 LIP
#
# Author: Mario David <mariojmdavid@gmail.com>
#

"""Create initial hdf5 files to store accounting data

    Dictionaries (data structures) returned from the query to database tables
    - projects  (DB=keystone, TABLE=project)
    - instances (DB=nova,     TABLE=instances)
    - volumes   (DB=cinder,   TABLE=volumes)
    project = { "description": None,
                "enabled": None,
                "id": None,
                "name": None
               }
    instances = {
                }
    volumes = {
              }
"""

from osacc_functions import *

if __name__ == '__main__':
    ev = get_conf()
    year = ev['year_ini']
    di = ev['secepoc_ini']
    df = now_acc()
    time_array_all = time_series(ev, di, df)
    state = "init"  # state is either "init" if first time accounting or "upd"
    projects_in = list()  # fill list of project ID when processing instances or volumes
    array_metrics = dict()  # array with metrics for each project
    p_dict = get_projects(di, state)
    process_inst(ev, di, df, time_array_all, array_metrics, p_dict, projects_in, state)
    process_vol(ev, di, df, time_array_all, array_metrics, p_dict, projects_in, state)
    directory = os.path.dirname(ev['out_dir'])
    if not os.path.exists(directory):
        os.makedirs(directory, 0o755)

    filename = create_hdf(ev, year)
    print("="*80)
    print(">>>> file created: ", filename)
    with h5py.File(filename, 'r+') as f:
        ts = f['date'][:]
        idx_start = time2index(ev, ts[0], time_array_all)
        idx_end = time2index(ev, df, time_array_all) + 1
        idx_start_ds = time2index(ev, ts[0], ts)
        idx_end_ds = time2index(ev, df, ts) + 1
        if year < years[-1]:
            idx_end = time2index(ev, ts[-1], time_array_all) + 1
            idx_end_ds = time2index(ev, ts[-1], ts) + 1

        for proj_id in projects_in:
            create_proj_datasets(ev, year, proj_id, p_dict)
            grp_name = p_dict[proj_id][0]
            for metric in METRICS:
                data_array = f[grp_name][metric]
                data_array[idx_start_ds:idx_end_ds] = array_metrics[grp_name][metric][idx_start:idx_end]

        f.attrs['LastRun'] = ts[idx_end_ds-1]
        f.attrs['LastRunUTC'] = str(to_isodate(ts[idx_end_ds-1]))
