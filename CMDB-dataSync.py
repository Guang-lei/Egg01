#!/usr/bin/env python

# SCRIPT_UUID = SC2024052015330801d1d7f40

import json
import socket
import subprocess
import sys
import time

import requests

# global params
METHOD_GET = 'GET'
METHOD_POST = 'POST'
METHOD_DELETE = 'DELETE'
METHOD_PATCH = 'PATCH'
METHOD_PUT = 'PUT'

# inputs params
xmly_endpoint = 'cmdb.pd.ximalaya.local'


def _get_host_name():
    host_name = socket.getfqdn(socket.gethostname())
    return host_name


def _common_http_request(url, method, headers=None, data=None):
    headers = {} if headers is None else headers
    try:
        if data is not None:
            data = json.dumps(data)
        resp = requests.request(method, url, data=data, headers=headers, verify=False)
        return resp
    except Exception as ex:
        print("Execute error: ", str(ex))
        raise ex


def _get_metedata():
    command = "curl http://169.254.169.254/openstack/latest/meta_data.json"
    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = result.communicate()
    result1 = json.loads(output)
    return result1


def _manual_synccmdb(regionId):
    if regionId == "hwyun":
        url = "http://{xmly}/cmdb-web/machineManage/provider/salt/sync?saltId=4".format(xmly=xmly_endpoint)
        resp = _common_http_request(url=url, method=METHOD_GET)
        if int(resp.status_code) == 200:
            print("hwyun synchronize CMDB successed: ", resp.status_code)
        else:
            print("hwyun synchronize CMDB failed: ", resp.status_code)
            sys.exit(1)
    if regionId == "cn-east-3":
        url = "http://{xmly}/cmdb-web/machineManage/provider/salt/sync?saltId=6".format(xmly=xmly_endpoint)
        resp = _common_http_request(url=url, method=METHOD_GET)
        if int(resp.status_code) == 200:
            print("hwyun-sh synchronize CMDB successed: ", resp.status_code)
        else:
            print("hwyun-sh synchronize CMDB failed: ", resp.status_code)
            sys.exit(1)


def _get_infofromcmdb(hostname):
    url = "http://{xmly}/cmdb-web/machineManage/provider/machineInfo?name={host_name}".format(xmly=xmly_endpoint,
                                                                                              host_name=hostname)
    resp = _common_http_request(url=url, method=METHOD_GET)
    if int(resp.status_code) == 200:
        result = json.loads(resp.content)
        data = result["data"]
        print("get host from cmdb success:", data)
        return data
    else:
        print("get memory error: ", resp.status_code)
        sys.exit(1)


def _retry():
    for i in range(3):
        _manual_synccmdb(regionId)
        data = _get_infofromcmdb(hostname)
        if data is not None:
            break
        time.sleep(5)
    if data is None:
        print("retry 3 time does not get host data")
        sys.exit(1)


if __name__ == "__main__":
    metedata = _get_metedata()
    regionId = metedata.get("region_id")
    hostname = _get_host_name()
    _retry()