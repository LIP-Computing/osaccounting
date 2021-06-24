#!/usr/bin/env python3

# -*- encoding: utf-8 -*-
#
# Copyright 2021 LIP
#
# Author: Mario David <mariojmdavid@gmail.com>
#
"""Get current resource usage for all projects
"""

import h5py
import osacc_functions as oaf


if __name__ == '__main__':

    ev = oaf.get_conf()
    filename = oaf.get_hdf_filename(ev)
    print('Filename:', filename)
    to_ns = 1000*1000*1000
    with h5py.File(filename, 'r') as f:
        tf = f.attrs['LastRun']
        ts = f['date'][:]
        len_ds = len(ts)
        csvstr = 'project,vcpus,volume_gb,ninstances,mem_mb,npublic_ips\n'
        for group in f:
            if group == "date":
                continue

            idx_end = oaf.time2index(ev, tf, ts)
            dgroup = f[group]
            csvstr = csvstr + group + ',' + str(dgroup['vcpus'][idx_end]) + ','
            csvstr = csvstr + str(dgroup['volume_gb'][idx_end]) + ',' + str(dgroup['ninstances'][idx_end]) + ','
            csvstr = csvstr + str(dgroup['mem_mb'][idx_end]) + ',' + str(dgroup['npublic_ips'][idx_end]) + '\n'

    print(csvstr)
