#!/usr/bin/env bash

# this script just records the total amount of object storage for a given project
# the openstack credentials, including the project, is set as argument to the script

if [ $# -ne 1 ]
then
    echo "Usage: $0 <openstack_cred_file>"
    exit 1
fi

. ${1}
eval $(openstack object store account show -f shell | sed 's/ *= */=/g')
date_sec_epoch=`date +%s`
date_now=`date +%d-%b-%Y-%H:%M:%S`
echo "${date_now},${date_sec_epoch},${bytes}"
