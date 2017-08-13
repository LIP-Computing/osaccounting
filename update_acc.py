# -*- encoding: utf-8 -*-
#
# Copyright 2017 LIP
#
# Author: Mario David <mariojmdavid@gmail.com>
#


"""Update accounting
"""

import datetime
from osacc_functions import *

if __name__ == '__main__':
    evr = get_env()
    year = datetime.datetime.now().year
    filename = get_hdf_filename(year)
    if not exists_hdf(year):
        filename = create_hdf(year)

    with h5py.File(filename, 'r+') as f:
        ti = f.attrs['LastRun']
        tf = today()
        projects = get_list_db("keystone", "project")
        instances = get_list_db("nova", "instances")
        volumes = get_list_db("cinder", "volumes")
        size_a = size_array(year)
        print 80 * "="
        print "Year = %i : Size Array = %i : FileName = %s" % (year, size_a, filename)
        print "Last Run = ", ti
        """
        print "--> Projects"
        pprint.pprint(projects)
        print
        print "--> Instances"
        pprint.pprint(instances)
        print
        print "--> Volumes"
        pprint.pprint(volumes)
        """
        print 20 * "-"

        ts = f['date'][:]
        print "Start date <ts>- ", to_isodate(ts[0])
        # This block is to insert the values from Nova Instances
        for inst in instances:
            t_create = to_secepoc(inst["created_at"])
            t_final = ts[size_a-1]
            if inst["deleted_at"]:
                t_final = to_secepoc(inst["deleted_at"])
            if t_final > to_secepoc(datetime.datetime.utcnow()):
                t_final = to_secepoc(datetime.datetime.utcnow())

            idx_start, idx_end = dt_to_indexes(t_create, t_final, year)
            p = filter(lambda pr: pr['id'] == inst['project_id'], projects)
            if not p:
                continue

            proj = p[0]
            grp_name = proj['name']
            vcpu_array = f[grp_name]['vcpus']
            vcpu_array[idx_start:idx_end] = vcpu_array[idx_start:idx_end] + inst['vcpus']
            mem_array = f[grp_name]['mem_mb']
            mem_array[idx_start:idx_end] = mem_array[idx_start:idx_end] + inst['memory_mb']
            disk_array = f[grp_name]['disk_gb']
            disk_array[idx_start:idx_end] = disk_array[idx_start:idx_end] + inst['root_gb']
            ninst_array = f[grp_name]['ninstances']
            ninst_array[idx_start:idx_end] = ninst_array[idx_start:idx_end] + 1

            print 80*'-'
            print 10*"x", " Instance ID = ", inst['uuid']
            print "ProjID Inst = ", inst['project_id'], " VCPUs= ", inst['vcpus'], " Mem_MB= ", inst['memory_mb']
            print "ProjID filt = ", proj["id"], proj["name"]
            print 'IDX_Start = ', idx_start, ' IDX_End = ', idx_end
            print 'Inst Start = ', to_isodate(t_create),      ' Inst End = ', to_isodate(t_final)
            print 'TS_Start   = ', to_isodate(ts[idx_start]), ' TS_End   = ', to_isodate(ts[idx_end])
            print 'VCPU Array Start = ', vcpu_array[idx_start], ' MEM Array Start = ', mem_array[idx_start]
            print "Number of instances = ", ninst_array[idx_start]

        # This block is to insert the values from Cinder volumes
        for vol in volumes:
            t_create = to_secepoc(vol["created_at"])
            t_final = ts[size_a-1]
            if vol["deleted"]:
                t_final = to_secepoc(vol["deleted_at"])
            if t_final > to_secepoc(datetime.datetime.utcnow()):
                t_final = to_secepoc(datetime.datetime.utcnow())

            idx_start, idx_end = dt_to_indexes(t_create, t_final, year)
            p = filter(lambda pr: pr['id'] == vol['project_id'], projects)
            if not p:
                continue

            proj = p[0]
            grp_name = proj['name']
            vol_array = f[grp_name]['volume_gb']
            vol_array[idx_start:idx_end] = vol_array[idx_start:idx_end] + vol['size']
            nvol_array = f[grp_name]['nvolumes']
            nvol_array[idx_start:idx_end] = nvol_array[idx_start:idx_end] + 1

            print 80*'-'
            print 10*"x", " Volume ID = ", vol['id']
            print "ProjID Vol  = ", vol['project_id'], " SizeGB= ", vol['size']
            print "ProjID filt = ", proj["id"], proj["name"]
            print 'IDX_Start = ', idx_start, ' IDX_End = ', idx_end
            print 'Vol Start = ', to_isodate(t_create),      ' Vol End = ', to_isodate(t_final)
            print 'TS_Start  = ', to_isodate(ts[idx_start]), ' TS_End  = ', to_isodate(ts[idx_end])
            print 'Vol Array Start = ', vol_array[idx_start], " Number of volumes = ", nvol_array[idx_start]