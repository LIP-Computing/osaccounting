#!/usr/bin/env bash

date_ini=`ate +%Y-%m-%d -d "last Sun -7 days"`
date_end=`date +%Y-%m-%d -d "last Sun"`
mkdir -p /var/log/osacc
/usr/local/bin/period_acc.py cloud_weekly date_ini date_end
echo "$? : period_acc.py cloud_monthly date_ini date_end"
DATE=`date +%F_%H-%M`
