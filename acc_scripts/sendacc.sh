#!/usr/bin/env bash

date
mkdir -p /var/log/osacc
/usr/local/bin/send_influx.py
echo "$? : send_influx.py"
DATE=`date +%F_%H-%M`
