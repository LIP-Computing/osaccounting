# -*- encoding: utf-8 -*-
#
# Copyright 2017 LIP
#
# Author: Mario David <mariojmdavid@gmail.com>
#


"""Send accounting data to graphite
"""

import socket
import struct

try:
    import cPickle as pickle
except ImportError:
    import pickle

from osacc_functions import *

if __name__ == '__main__':
    ev = get_conf()
    carbon_server = ev['carbon_server']
    carbon_port = ev['carbon_port']
    graph_ns = ev['graph_ns']
    send_inter = ev['send_inter']
    ini_list = 60  # size of list to send
    now = datetime.datetime.utcnow()
    year = now.year
    delay = 0  # seconds delay to close connection
    max_retries = 3  # number of retries for socket connect
    timeout = 3  # seconds between retries for socket connect
    print 80 * "="
    filename = get_hdf_filename(ev, year)
    print " Filename = ", filename
    with h5py.File(filename, 'r') as f:
        df = int(f.attrs['LastRun'])
        di = df - send_inter
        ts = f['date'][:]
        idx_start_ds = time2index(ev, di, ts)
        idx_end_ds = time2index(ev, df, ts) + 1
        print "di =", di, " df =", df
        print "idx =", idx_start_ds, idx_end_ds
        print "di =", to_isodate(ts[idx_start_ds]), " df =", to_isodate(ts[idx_end_ds])
        for group in f:
            if group == "date":
                continue
            for m in METRICS:
                print "Project =", group, " metric =", m
                graph_list = list()
                data = f[group][m]
                metric_str = graph_ns + "." + str(group) + "." + str(m)
                for i in range(idx_start_ds, idx_end_ds):
                    graph_string = metric_str + " " + str(data[i]) + " " + str(int(ts[i])) + "\n"
                    value = int(data[i])
                    timestamp = int(ts[i])
                    metric = str(metric_str)
                    graph_ds = (metric, (timestamp, value))
                    graph_list.append(graph_ds)
                    if (i % ini_list == 0) or (i == idx_end_ds - 1):
                        package = pickle.dumps(graph_list, protocol=2)
                        size = struct.pack('!L', len(package))
                        message = size + package
                        print 5*"#"
                        print "i =", i, " Length =", len(graph_list), " Size =", len(package), " date =", to_isodate(timestamp)
                        sock = socket.socket()
                        for j in range(max_retries):
                            try:
                                sock.connect((carbon_server, carbon_port))
                                sock.sendall(message)
                                time.sleep(delay)
                            except IOError as e:
                                print "Couldn't connect to %(server)s on port %(port)d. Retry: %(j)i" % {
                                    'server': carbon_server, 'port': carbon_port, 'j': j}
                                continue
                            else:
                                sock.close()
                                break

                        graph_list = list()