#!/usr/bin/env bash

date
mkdir -p /var/log/osinfo
/usr/local/bin/osinfo2md.py /var/log/osinfo/data.json /var/log/osinfo/
echo "$? : osinfo2md.py"

