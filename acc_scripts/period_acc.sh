#!/usr/bin/env bash

mkdir -p /var/log/osacc
/usr/local/bin/period_acc.py
echo "$? : period_acc.py"
DATE=`date +%F_%H-%M`
