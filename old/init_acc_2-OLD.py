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
    years = get_years()
    di = ev['secepoc_ini']
    df = to_secepoc(datetime.datetime(years[-1]+1, 1, 1, 0, 0, 0))
    time_array = time_series(di, df)
    a = dict()

    projects = get_list_db(di, "keystone")
    for proj in projects:
        pname = proj['name']
        a[pname] = dict()
        for m in METRICS:
            a[pname][m] = numpy.zeros([time_array.size, ], dtype=int)

    instances = get_list_db(di, "nova")
    for inst in instances:
        t_create = to_secepoc(inst["created_at"])
        t_final = now_acc()
        if inst["deleted_at"]:
            t_final = to_secepoc(inst["deleted_at"])

        idx_start, idx_end = dt_to_index(t_create, t_final, time_array)
        p = filter(lambda pr: pr['id'] == inst['project_id'], projects)
        if not p:
            continue

        proj = p[0]
        pname = proj['name']
        a[pname]['vcpus'][idx_start:idx_end] = a[pname]['vcpus'][idx_start:idx_end] + inst['vcpus']
        a[pname]['mem_mb'][idx_start:idx_end] = a[pname]['mem_mb'][idx_start:idx_end] + inst['memory_mb']
        a[pname]['disk_gb'][idx_start:idx_end] = a[pname]['disk_gb'][idx_start:idx_end] + inst['root_gb']
        a[pname]['ninstances'][idx_start:idx_end] = a[pname]['ninstances'][idx_start:idx_end] + 1
        net_info = json.loads(inst['network_info'])
        if net_info:
            for l in range(len(net_info)):
                for n in range(len(net_info[l]['network']['subnets'])):
                    for k in range(len(net_info[l]['network']['subnets'][n]['ips'])):
                        nip = len(net_info[l]['network']['subnets'][n]['ips'][k]['floating_ips'])
                        a[pname]['npublic_ips'][idx_start:idx_end] = a[pname]['npublic_ips'][idx_start:idx_end] + nip

    volumes = get_list_db(di, "cinder")
    for vol in volumes:
        t_create = to_secepoc(vol["created_at"])
        t_final = now_acc()
        if vol["deleted_at"]:
            t_final = to_secepoc(vol["deleted_at"])

        idx_start, idx_end = dt_to_index(t_create, t_final, time_array)
        p = filter(lambda pr: pr['id'] == vol['project_id'], projects)
        if not p:
            continue

        proj = p[0]
        pname = proj['name']
        a[pname]['volume_gb'][idx_start:idx_end] = a[pname]['volume_gb'][idx_start:idx_end] + vol['size']
        a[pname]['nvolumes'][idx_start:idx_end] = a[pname]['nvolumes'][idx_start:idx_end] + 1

    directory = os.path.dirname(ev['out_dir'])
    if not os.path.exists(directory):
        os.makedirs(directory, 0755)

    years = get_years()
    for year in years:
        filename = create_hdf(year)
        with h5py.File(filename, 'r+') as f:
            ts = f['date'][:]
            idx_start, idx_end = dt_to_index(ts[0], ts[-1], time_array)
            for proj in projects:
                grp_name = proj['name']
                for metric in METRICS:
                    data_array = f[grp_name][metric]
                    data_array[:] = a[grp_name][metric][idx_start:idx_end+1]

            tnow = now_acc()
            f.attrs['LastRun'] = tnow
            f.attrs['LastRunUTC'] = str(to_isodate(tnow))
            if year < years[-1]:
                f.attrs['LastRun'] = ts[-1]
                f.attrs['LastRunUTC'] = str(to_isodate(ts[-1]))