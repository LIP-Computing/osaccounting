# Accounting for Openstack

Accounting for Openstack, uses hdf5 to store time series of number of VCPUs, amount of memmory,
amount of local disk, number and size of cinder volumes, per Openstack project.

The script `get_acc.py`, queries the Openstack databases: `keystone`, `nova` and `cinder`, to get
the projects and respective metrics and writes them into hdf5 files in the form of a time series.

The script `send_elasticsearch.py`, reads the metrics from the produced hdf5 files and send them
into Elasticsearch database, and `send_influx.py` sends them to Influxdb.

Several additional scripts will be explained below.

## Configuration

The scripts rely on environment variables:

* OUT_DIR - output directory for projects.json, also for the accounting files the default value is '/tmp' 
* MYSQL_USER - database user to get the records from the cinder DB
* MYSQL_PASS - database password for the cinder DB
* MYSQL_HOST - database host

## Usage

The script setup.sh deploys the scripts in /usr/local/bin and a configuration file to setup the necessary environment
variables osacc-conf.sh into /etc

```bash
./setup.sh
```

## Current resource usage

The script `res_usage.py` should be in `root@stratus-001.ncg.ingrid.pt:/usr/local/bin/` it has the options set in the
configuration file `/etc/osacc.conf` and read the hdf5 files that are updated from the accounting: `/var/log/osacc/osacc.hdf`

```bash
source /usr/local/py3/bin/activate
python /usr/local/bin/res_usage.py
```

Prints a csv that you can copy into a spreadsheet.
