#!/usr/bin/env bash

mkdir -p /var/log/osacc
/usr/local/bin/period_acc.py weekly
echo "$? : period_acc.py weekly"
DATE=`date +%F_%H-%M`
