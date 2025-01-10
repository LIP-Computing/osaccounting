#!/usr/bin/env bash

date_ini=`date`
date_end=`date`
mkdir -p /var/log/osacc
/usr/local/bin/period_acc.py cloud_monthly date_ini date_end
echo "$? : period_acc.py cloud_monthly date_ini date_end"
DATE=`date +%F_%H-%M`
