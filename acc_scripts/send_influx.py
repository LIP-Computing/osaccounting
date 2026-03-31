#!/usr/bin/env python3

# -*- encoding: utf-8 -*-
#
# Copyright 2020 LIP
#
# Author: Mario David <mariojmdavid@gmail.com>
#
"""Send metric to influxdb
"""
import os
import dateutil.parser
import h5py
from datetime import datetime
from pprint import pprint
from influxdb_client import InfluxDBClient, Point, WritePrecision, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError
import osacc_functions as oaf


class BatchingCallback(object):
    def success(self, conf: (str, str, str), data: str):
        print(f"Written batch: {conf} - number of data points: {len(data)}")

    def error(self, conf: (str, str, str), data: str, exception: InfluxDBError):
        print(f"Cannot write batch: {conf} due: {exception} - number of data points: {len(data)}")

    def retry(self, conf: (str, str, str), data: str, exception: InfluxDBError):
        print(f"Retryable error occurs for batch: {conf} retry: {exception} - number of data points: {len(data)}")


def get_last(ev, group):
    """Get last metric timestamp from DB
    :param ev: Configuration options list
    :param client: InfluxDB client
    :param group: project
    :return (datetime) last timestamp in seconds to epoc
    """
    # qry_str = 'SELECT last(vcpus) FROM cloud_acc WHERE project=$proj'
    # bind_params = {'proj': group}
    # last_ts = client.query(qry_str, bind_params=bind_params)
    # if last_ts:
    #     time_stamp = last_ts.get_points()
    #     for t in time_stamp:
    #         a = dateutil.parser.parse(t["time"])
    #         ti = oaf.to_secepoc(a)

    # dt_ini = datetime(2026, 3, 30, 13, 0, 0)

    ti = ev['secepoc_ini']
    return ti


if __name__ == '__main__':
    ev = oaf.get_conf()
    dbhost = ev['dbhost']
    dbport = ev['dbport']
    dbtoken = ev['dbtoken']
    dborg = ev['dborg']
    bssl = ev['ssl']
    bverify_ssl = ev['verify_ssl']
    baseurl = f'https://{dbhost}:{dbport}'
    wrt_opt = WriteOptions(batch_size=5000,
                           flush_interval=10_000,
                           jitter_interval=2_000,
                           retry_interval=5_000,
                           max_retries=5,
                           max_retry_delay=30_000,
                           exponential_base=2)

    filename = oaf.get_hdf_filename(ev)
    print(80 * '=')
    print('Filename:', filename)
    with h5py.File(filename, 'r') as f:
        tf = f.attrs['LastRun']
        ts = f['date'][:]
        len_ds = len(ts)
        print(f'Last run timestamp: {tf} - number of ts points: {len_ds}')
        for group in f:
            lpoints = []
            print(group)
            if group == "date":
                continue

            ti = get_last(ev, group)
            idx_start = oaf.time2index(ev, ti, ts)
            idx_end = oaf.time2index(ev, tf, ts)
            print(20*'+')
            print(f'Group: {group} - idx_start: {idx_start} - idx_end: {idx_end}')
            dgroup = f[group]
            for i in range(idx_start, idx_end+1):
                point = Point('cloud_acc').tag('project', group) \
                        .field('vcpus', dgroup['vcpus'][i]) \
                        .field('mem_mb', dgroup['mem_mb'][i]) \
                        .field('volume_gb', dgroup['volume_gb'][i]) \
                        .field('ninstances', dgroup['ninstances'][i]) \
                        .field('nvolumes', dgroup['nvolumes'][i]) \
                        .field('npublic_ips', dgroup['npublic_ips'][i]) \
                        .field('q_vcpus', dgroup.attrs['q_vcpus']) \
                        .field('q_mem_mb', dgroup.attrs['q_mem_mb']) \
                        .field('q_volume_gb', dgroup.attrs['q_volume_gb']) \
                        .field('q_ninstances', dgroup.attrs['q_ninstances']) \
                        .field('q_nvolumes', dgroup.attrs['q_nvolumes']) \
                        .field('q_npublic_ips', dgroup.attrs['q_npublic_ips']) \
                        .time(int(ts[i]), WritePrecision.S)

                lpoints.append(point)

            with InfluxDBClient(url=baseurl, token=dbtoken, org=dborg, ssl=bssl, verify_ssl=bverify_ssl) as client:
                bcb = BatchingCallback()
                with client.write_api(success_callback=bcb.success, error_callback=bcb.error, retry_callback=bcb.retry) as write_api:
                    write_api.write(bucket="openstack", record=lpoints, write_precision=WritePrecision.S)
