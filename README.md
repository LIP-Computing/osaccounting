# Accounting for Openstack

Accounting for Openstack, uses hdf5 to store time series of number of VCPUs, amount of memmory,
amount of local disk, number and size of cinder volumes, per Openstack project.

* `get_acc.py` - This script queries the Openstack databases: `keystone`, `nova` and `cinder`,
  to get the projects and respective metrics and writes them into hdf5 files in the form of a time
  series.
* `send_elasticsearch.py` - This script reads the metrics from the produced hdf5 files and send them
  into Elasticsearch database
* `send_influx.py` - sends them to Influxdb.
* `osacc_functions.py` - has all the functions used by the other scripts.

## Other scripts

All these scripts have the hdf5 file as input, to process the accounting data:

* `res_usage.py` - prints a CSV with the current resource usage per project.
* `period_acc.py` - write a CSV file with monthly resource consumption per project.
  * `process_month.py` - read the CSV from the previous script and produces a CSV with VCPU*hours
    per project, and another CSV with TB*month per project.

## Configuration

The scripts rely on environment variables:

* [DEFAULT] - Mandatory
  * `OUT_DIR` - output directory for projects.json, also for the accounting files and logs, the
    default value is '/tmp'.
  * `MONTH_INI` and `YEAR_INI` - initial month and year to start the accounting.
  * `DELTA_TIME` - Interval between metric timestamps in seconds.
* [mysql] - Mandatory
  * `MYSQL_USER` - database user to get the records from the cinder DB.
  * `MYSQL_PASS` - database password for the cinder DB.
  * `MYSQL_HOST` - database host.
* [osinfo] - Mandatory for the script `osinfo.py`
  * `UFILE_DIR` - Openstack Info directory with users files.
* [elasticsearch] - Optional, only used if you send to EleasticSearch.
  * ESHOST - ElasticSearch endpoint.
  * ESINDEX - ElasticSearch index for accounting.
  * ESAPIKEY - ElasticSearch API key
* [influxdb] - Optional, only used if you send to InfluxDB.
  * `DBHOST` - database host.
  * `DBPORT` - database port.
  * `DBUSER` - database user.
  * `DBPASS` - database password.
  * `DBNAME` - database name for accounting.
  * `SSL` - if you use cert to assess the database.
  * `VERIFY_SSL` - if client uses certificate to connect to database.

## Current resource usage

The script `res_usage.py` should be in `root@stratus-001.ncg.ingrid.pt:/usr/local/bin/` it has the options set in the
configuration file `/etc/osacc.conf` and read the hdf5 files that are updated from the accounting: `/var/log/osacc/osacc.hdf`

```bash
source /usr/local/py3/bin/activate
python /usr/local/bin/res_usage.py
```

Prints a csv that you can copy into a spreadsheet.
