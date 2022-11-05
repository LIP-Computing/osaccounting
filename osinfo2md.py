#!/usr/bin/env python3

# -*- encoding: utf-8 -*-
#
# Copyright 2019 LIP
#
# Author: Mario David <mariojmdavid@gmail.com>
#

"""Produce a Markdown document from the osinfo.py json
osinfo_json =
[
    {
        "timestamp": "timestamp",
        "project_id": "string",
        "project_name": "string",
        "project_description": "string",
        "users": [
            {
                "id": "string",
                "username": "string",
                "email": "string",
                "description": "string",
                "created_at": "timestamp",
                "created": bool
            },
        ],
        "servers": [
            {
                "uuid": "string",
                "hostname": "string",
                "description": "string",
                "created_at": "timestamp",
                "key_name": "string",
                "fixed_ips": [],
                "floating_ips": []
            },
        ],
        "storage": [
            {
                "type": "<volume|snapshot|image>",
                "id": "string",
                "name": "string",
                "display_description": "string",
                "size": "int (GB)",
                "status": "string",
                "created_at": "datetime"
            },
        ],
    },
]
"""
import sys
import json
import pprint
import datetime


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Error json file not specified: %s <data.json>' %sys.argv[0])
        sys.exit(1)

    json_file = sys.argv[1]
    with open(json_file, 'r') as outjson:
        data = json.load(outjson)

    md = ''
    hdrproj = '\n| **Date** | **Project description** | **Project ID** |\n'
    hdrproj = hdrproj + '| - | - | - |\n'
    hdruser = '\n\n### Users\n| **Created** | **email** | **Name** |\n'
    hdruser = hdruser + '| - | - | - |\n'
    hdrserver = '\n\n### VMs\n| **Created** | **Hostname** | **Description** | **Fixed IP** | **Public IP** |\n'
    hdrserver = hdrserver + '| - | - | - | - | - |\n'
    hdrvol = '\n\n### Volumes\n| **Created** | **Size (GB)** | **Type** | **Status** | **Cinder ID** |\n'
    hdrvol = hdrvol + '| - | - | - | - | - |\n'
    users_str = 'project,name,email\n'
    for project in data:
        md = md + '## Project: ' + project['project_name'] + '\n\n'
        md = md + hdrproj
        dtime = datetime.datetime.utcfromtimestamp(project['timestamp'])
        rowproj = '| ' + str(dtime) + ' | ' + project['project_description']
        rowproj = rowproj + ' | ' + project['project_id'] + ' |\n\n'
        md = md + rowproj
        md = md + hdruser
        for user in project['users']:
            if user['email'] is None:
                continue
            rowuser = '| ' + str(user['created']) + ' | ' + user['email'] + ' | '
            rowuser = rowuser + user['description'] + ' |\n'
            md = md + rowuser
            users_str = users_str + project['project_name'] + ',' + user['description']+ ',' + user['email'] + '\n'

        md = md + '\n'
        md = md + hdrserver
        for server in project['servers']:
            pubip = ''
            serdesc = ''
            if isinstance(server['description'], str):
                serdesc = server['description']
            if isinstance(server['floating_ips'], list):
                if len(server['floating_ips']) == 1:
                    pubip = server['floating_ips'][0]

            rawvm = '| ' + str(datetime.datetime.utcfromtimestamp(server['created_at'])) + ' | '
            rawvm = rawvm + server['hostname'] + ' | ' + serdesc + ' | '
            rawvm = rawvm + server['fixed_ips'][0] + ' | ' + pubip + ' |\n'
            md = md + rawvm

        md = md + '\n'
        md = md + hdrvol
        for vol in project['storage']:
            rawvol = '| ' + str(datetime.datetime.utcfromtimestamp(vol['created_at'])) + ' | '
            rawvol = rawvol + str(vol['size']) + ' | ' + vol['type'] + ' | '
            rawvol = rawvol + vol['status'] + ' | ' + vol['id'] + ' |\n'
            md = md + rawvol

        md = md + '\n'

    header = ('## Howto create this markdown'
              ''
              '* `openstack user list --long -c Name -c Description -c Email -c Enabled -f csv --project <PROJECT_NAME>`'
              '* Update file in gitlab repo: <https://git01.a.incd.pt/lip-computing/openstack-deploy/-/blob/master/playbooks-prod/files/users-stratus-disabled.csv>'
              '* scp this file to stratus-001: `scp users-stratus-disabled.csv root@stratus-001.ncg.ingrid.pt:/etc/`'
              '* Execute the script in stratus-001 `/usr/local/bin/osinfo.sh >> /var/log/osinfo/osinfo.log 2>&1`'
              '* scp the file to your desktop: `scp root@stratus-001.ncg.ingrid.pt:/var/log/osinfo/data.json ~/`'
              '* clone the git repo: `git clone git@github.com:LIP-Computing/osaccounting.git`'
              '* `cd osaccounting`'
              '* Execute the script to produce this md: `python osinfo2md.py ~/data.json`'
              '\n\nupdate md')
    md = header + md
    with open('osinfo.md', 'w') as fd:
        fd.write(md)

    with open('usersall.csv', 'w') as fd:
        fd.write(users_str)

    sys.exit(0)
