#!/usr/bin/env python3

# -*- encoding: utf-8 -*-
#
# Copyright 2019 LIP
#
# Author: Mario David <mariojmdavid@gmail.com>
#
# DEPRECATION info
# '* Update file in gitlab repo: <https://gitlab-admin.a.incd.pt/lip-computing/openstack-deploy/-/blob/master/playbooks-prod/files/users-stratus-disabled.csv>\n'
# '* scp this file to stratus-001: `scp users-stratus-disabled.csv root@stratus-001.ncg.ingrid.pt:/etc/`\n'
#
# This script is prepared to run on any of the Openstack controller nodes with input data.json produced with osinfo.py,
# it is expected to have access to /etc/openstack-dashboard/local_settings.py

"""Produce a Markdown document from the osinfo.py json
osinfo_json =
[
    {
        "timestamp": "timestamp",
        "project_id": "string",
        "project_name": "string",
        "project_description": "string",
        "tot_nvcpus": "int",
        "tot_ram_gb": "int",
        "tot_npub_ips": "int",
        "tot_stor": "int (GB)",
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
                "host": "string",
                "fixed_ips": [],
                "floating_ips": []
                "nvcpus",
                "ram_gb",
                "npub_ips"
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
        print('Error json file not specified: %s <data.json>' % sys.argv[0])
        sys.exit(1)

    osdashconf = "/etc/openstack-dashboard/local_settings.py"
    if os.path.isfile(osdashconf):
        with open(osdashconf, 'r') as fp:
            for l_no, line in enumerate(fp):
                if 'OPENSTACK_HOST' in line:
                    osinfra = line.split('=')[1]
                    break

    print(osinfra)

    json_file = sys.argv[1]
    with open(json_file, 'r') as outjson:
        data = json.load(outjson)

    md = ''
    hdrproj = '\n| **Date** | **Project description** | **Project ID** |\n'
    hdrproj = hdrproj + '| - | - | - |\n'

    hdruser = '\n\n### Users\n| **Created** | **email** | **Name** |\n'
    hdruser = hdruser + '| - | - | - |\n'

    hdrres = '\n\n### Resources\n| **Total VCPUs** | **Total RAM (GB)** | **Total Public IPs** | **Total Storage (GB)**|\n'
    hdrres = hdrres + '| - | - | - | - |\n'

    hdrserver = '\n\n### VMs\n| **Created** | **Hostname** | **Description** | **VCPUs** | **RAM (GB)** | **Fixed IP** | **Public IP** |\n'
    hdrserver = hdrserver + '| - | - | - | - | - | - | - |\n'

    hdrvol = '\n\n### Volumes\n| **Created** | **Size (GB)** | **Type** | **Status** | **Cinder ID** |\n'
    hdrvol = hdrvol + '| - | - | - | - | - |\n'

    resource_str = 'project,vcpus,stor,memory,ips\n'

    for project in data:
        md = md + '\n## Project: ' + project['project_name'] + '\n\n'
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

        md = md + hdrres
        rawres = '| ' + str(project['tot_nvcpus']) + ' | ' + str(project['tot_ram_gb']) + ' | '
        rawres = rawres + str(project['tot_npub_ips']) + ' | ' + str(project['tot_stor']) + ' |\n'
        md = md + rawres

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
                else:
                    pubip = 'n.a.'

            if len(server['fixed_ips']) == 0:
                continue

            rawvm = '| ' + str(datetime.datetime.utcfromtimestamp(server['created_at'])) + ' | '
            rawvm = rawvm + server['hostname'] + ' | ' + serdesc + ' | '
            rawvm = rawvm + str(server['nvcpus']) + ' | ' + str(server['ram_gb']) + ' | '
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
        resource_str = resource_str + project['project_name'] + ',' + str(project['tot_nvcpus']) + ',' + str(project['tot_stor']) + ','
        resource_str = resource_str + str(project['tot_ram_gb']) + ',' + str(project['tot_npub_ips']) + '\n'

    header = '# Projects information for\n\n'
    md = header + md
    with open('osinfo.md', 'w') as fd:
        fd.write(md)

    with open('resourcesall.csv', 'w') as fd:
        fd.write(resource_str)

    sys.exit(0)
