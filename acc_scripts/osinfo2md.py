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
import os
import json
from datetime import datetime, timezone
import osacc_functions as oaf

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'Error json file not specified: {sys.argv[0]} <data.json> <output_dir>')
        sys.exit(1)

    ev = oaf.get_conf()
    osinfra = ev['openstack_host']
    json_file = sys.argv[1]
    out_dir = sys.argv[2] + '/'
    if not os.path.isdir(out_dir):
        print(f'Error dir {out_dir} not dir or not found')
        sys.exit(1)

    with open(json_file, 'r', encoding='utf-8') as outjson:
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

    hdrvol = '\n\n### Volumes\n| **Created** | **Name** | **Size (GB)** | **Type** | **Status** | **Cinder ID** |\n'
    hdrvol = hdrvol + '| - | - | - | - | - | - |\n'

    resource_str = 'project,vcpus,stor,memory,ips\n'
    res_str = ''
    tvcpus = 0
    tram = 0
    tips = 0
    tstor = 0

    for project in data:
        md = md + '\n## Project: ' + project['project_name'] + '\n\n'
        md = md + hdrproj
        dtime = datetime.fromtimestamp(project['timestamp'], tz=timezone.utc)
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

            rawvm = '| ' + str(datetime.fromtimestamp(server['created_at'], tz=timezone.utc)) + ' | '
            rawvm = rawvm + server['hostname'] + ' | ' + serdesc + ' | '
            rawvm = rawvm + str(server['nvcpus']) + ' | ' + str(server['ram_gb']) + ' | '
            rawvm = rawvm + server['fixed_ips'][0] + ' | ' + pubip + ' |\n'
            md = md + rawvm

        md = md + '\n'
        md = md + hdrvol
        for vol in project['storage']:
            rawvol = '| ' + str(datetime.fromtimestamp(vol['created_at'], tz=timezone.utc)) + ' | '
            rawvol = rawvol + str(vol['name']) + ' | ' + str(vol['size']) + ' | ' + vol['type'] + ' | '
            rawvol = rawvol + vol['status'] + ' | ' + vol['id'] + ' |\n'
            md = md + rawvol

        md = md + '\n'
        res_str += project['project_name'] + ',' + str(project['tot_nvcpus']) + ',' + str(project['tot_stor']) + ','
        res_str += str(project['tot_ram_gb']) + ',' + str(project['tot_npub_ips']) + '\n'
        tvcpus += project['tot_nvcpus']
        tram += project['tot_ram_gb']
        tips += project['tot_npub_ips']
        tstor += project['tot_stor']

    header = f'# Projects information for {osinfra}\n\n'
    md = header + md
    mdfile = out_dir + 'osinfo-' + osinfra + '.md'
    rescsv = out_dir + 'resourcesall-' + osinfra + '.csv'
    with open(mdfile, 'w', encoding='utf-8') as fd:
        fd.write(md)

    resource_str += 'total_used' + ',' + str(tvcpus) + ',' + str(tstor) + ',' + str(tram) + ',' + str(tips) + '\n'
    resource_str += res_str
    with open(rescsv, 'w', encoding='utf-8') as fd:
        fd.write(resource_str)

    sys.exit(0)
