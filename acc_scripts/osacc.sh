#!/usr/bin/env bash

date
mkdir -p /var/log/osacc
/usr/local/bin/get_acc.py
echo "$? : get_acc.py"
DATE=`date +%F_%H-%M`
