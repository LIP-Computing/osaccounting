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
        print(f"Written batch: {conf}")

    def error(self, conf: (str, str, str), data: str, exception: InfluxDBError):
        print(f"Cannot write batch: {conf} due: {exception}")

    def retry(self, conf: (str, str, str), data: str, exception: InfluxDBError):
        print(f"Retryable error occurs for batch: {conf} retry: {exception}")


def get_influxclient(ev):
    """Get InfluxDB Client
    :return: InfluxDB Client
    """
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

    # wco = write_client_options(success_callback=success,
    #                            error_callback=error,
    #                            retry_callback=retry)

    client = InfluxDBClient(url=baseurl, token=dbtoken,
                            org=dborg, ssl=bssl,
                            verify_ssl=bverify_ssl)

    wrt_api = client.write_api(write_options=wrt_opt)
    check_conn = client.ping()
    print(f'{baseurl} ping: {check_conn}')
    return wrt_api


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
    # ti = ev['secepoc_ini']
    # if last_ts:
    #     time_stamp = last_ts.get_points()
    #     for t in time_stamp:
    #         a = dateutil.parser.parse(t["time"])
    #         ti = oaf.to_secepoc(a)

    dt_ini = datetime(2026, 3, 30, 13, 0, 0)
    ti = oaf.to_secepoc(dt_ini)
    return ti


if __name__ == '__main__':
    ev = oaf.get_conf()
    filename = oaf.get_hdf_filename(ev)
    print(80 * '=')
    print('Filename:', filename)
    lpoints = []
    with h5py.File(filename, 'r') as f:
        tf = f.attrs['LastRun']
        ts = f['date'][:]
        len_ds = len(ts)
        print(f'Last run timestamp: {tf} - number of ts points: {len_ds}')
        data_met = []
        for group in f:
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

    # wco = write_client_options(success_callback=success,
    #                            error_callback=error,
    #                            retry_callback=retry)

    with InfluxDBClient(url=baseurl, token=dbtoken,
                        org=dborg, ssl=bssl,
                        verify_ssl=bverify_ssl) as client:
        callback = BatchingCallback()
        with client.write_api(success_callback=callback.success,
                              error_callback=callback.error,
                              retry_callback=callback.retry) as write_api:
            write_api.write(bucket="openstack", record=lpoints, write_precision=WritePrecision.S)



    # client = InfluxDBClient(url=baseurl, token=dbtoken,
    #                         org=dborg, ssl=bssl,
    #                         verify_ssl=bverify_ssl)

    # wrt_api = client.write_api(write_options=wrt_opt)


        # print(point.to_line_protocol())
        # make_mtr = [group]
        # make_mtr_quota = []
        # a = (i-idx_start) % batch_size
        # if not a:
        #     data_met = []
        # ['vcpus', 'mem_mb', 'volume_gb', 'ninstances', 'nvolumes', 'npublic_ips']
        # for mtr in oaf.METRICS:
        #     data = dgroup[mtr]
        #     data_quota = dgroup.attrs[f'q_{mtr}']
        #     make_mtr.append(data[i])
        #     make_mtr_quota.append(data_quota)

        # data_met.append(make_mtr + make_mtr_quota)

    # with h5py.File(filename, 'r') as f:
    #     tf = f.attrs['LastRun']
    #     ts = f['date'][:]
    #     len_ds = len(ts)
    #     for group in f:
    #         print(group)
    #         if group == "date":
    #             continue

    #         ti = get_last(ev, client, group)
    #         idx_start = oaf.time2index(ev, ti, ts)
    #         idx_end = oaf.time2index(ev, tf, ts)
    #         dgroup = f[group]
    #         for i in range(idx_start, idx_end+1):
    #             a = (i-idx_start) % batch_size
    #             if not a:
    #                 data_met = []

    #             make_mtr = "cloud_acc,project=" + group + " "
    #             for mtr in oaf.METRICS:
    #                 data = dgroup[mtr]
    #                 q_name = "q_" + mtr
    #                 q_value = dgroup.attrs[q_name]
    #                 make_mtr = make_mtr + mtr + "=" + str(data[i]) + ","
    #                 make_mtr = make_mtr + q_name + "=" + str(q_value) + ","

    #             infl_proj = make_mtr.rstrip(",")
    #             infl_proj = infl_proj + " " + str(int(ts[i]*to_ns))
    #             data_met.append(infl_proj)
    #             b = (i+1-idx_start) % batch_size
    #             if not b or (i == idx_end):
    #                 client.write_points(data_met, batch_size=batch_size, protocol='line')
