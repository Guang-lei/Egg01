#!/usr/bin/env python

# SCRIPT_UUID = SC202405201529480136e9119

import json
import os
import socket
import subprocess
import sys
import requests

# global params
METHOD_GET = 'GET'
METHOD_POST = 'POST'
METHOD_DELETE = 'DELETE'
METHOD_PATCH = 'PATCH'
METHOD_PUT = 'PUT'

# inputs params

iam_domain_name = os.getenv('iam_domain_name')
iam_user_name = os.getenv('iam_user_name')
iam_user_password = os.getenv('iam_user_password')
server_name_prefix = os.getenv('server_name_prefix')


def _init_host_ip():
    host_name = socket.getfqdn(socket.gethostname())
    ip = socket.gethostbyname(host_name)
    return ip


def _get_host_name():
    host_name = socket.getfqdn(socket.gethostname())
    return host_name


def _common_http_request(url, method, headers=None, data=None):
    headers = {} if headers is None else headers
    try:
        if data is not None:
            data = json.dumps(data)
        resp = requests.request(method, url, data=data, headers=headers)
        return resp
    except Exception as ex:
        print("Execute error: ", str(ex))
        raise ex


def _get_iam_token(projectId, iam_url):
    body = {
        'auth': {
            'identity': {
                'methods': [
                    'password'
                ],
                'password': {
                    'user': {
                        'name': iam_user_name,
                        'password': iam_user_password,
                        'domain': {
                            'name': iam_domain_name
                        }
                    }
                }
            },
            'scope': {
                'project': {
                    'id': projectId
                }
            }
        }
    }
    headers = {'Content-Type': 'application/json'}
    url = "https://{iam_url}/v3/auth/tokens".format(iam_url=iam_url)
    resp = _common_http_request(url=url, method=METHOD_POST, headers=headers, data=body)
    if int(resp.status_code) == 201:
        token = resp.headers['X-Subject-Token']
        return token
    else:
        print("get iamtoken error: ", resp.status_code)
        sys.exit(1)


def _get_server_id(token, bms_url, project_id, hostname):
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}

    url = "https://{bms_url}/v1/{project_id}/baremetalservers/detail?name={hostname}".format(
        bms_url=bms_url, project_id=project_id, hostname=hostname)
    resp = _common_http_request(url=url, method=METHOD_GET, headers=headers)
    if int(resp.status_code) == 200:
        result = json.loads(resp.content)
        return result["servers"][0]["id"].encode('utf-8')
    else:
        print("get serverid error: ", resp.status_code)
        sys.exit(1)


def _change_server_name_in_bms(token, bms_url, server_id, new_host_name, project_id):
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    url = "https://{bms_url}/v1/{project_id}/baremetalservers/{server_id}".format(
        bms_url=bms_url, project_id=project_id, server_id=server_id)
    # name: prefix + 6bit uuid
    body = {
        "server": {
            "name": new_host_name
        }
    }
    print("bms_url:", url)
    resp = _common_http_request(url=url, method=METHOD_PUT, headers=headers, data=body)
    if int(resp.status_code) == 200:
        result = json.loads(resp.content)
        changed_name = result["server"]['name']
        print("hostname in ECS Console now: ", changed_name.encode('utf-8'))
    else:
        print("error: ", resp.status_code)
        sys.exit(1)


def _get_metedata():
    command = "curl http://169.254.169.254/openstack/latest/meta_data.json"
    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = result.communicate()
    result1 = json.loads(output)
    return result1


def _change_local_hostname(new_host_name):
    command = "hostnamectl set-hostname {new_name}".format(new_name=new_host_name)
    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = result.communicate()
    print("hostname now: ", socket.gethostname())


def _get_new_name():
    metedata = _get_metedata()
    regionId = metedata.get("region_id")
    regionKey = {"cn-east-3": "sh1", "cn-north-4": "bj1"}
    az = metedata.get("availability_zone")
    chargingMode = metedata.get("meta", {}).get("charging_mode")
    azKey = {"a": "1", "b": "2", "c": "3", "d": "4"}
    epcKey = {"a": "2", "d": "1"}
    #chargingKey = {"0": "usage", "1": "month"}
    #new_host_name = regionKey.get(regionId) + "-" + azKey.get(az[-1]) + "-cloud-" + chargingKey.get(
    #    chargingMode) + "-" + server_name_prefix + "-" + host_ip.replace(".", "-") + ".ximalaya.hw"
    new_host_name = regionKey.get(regionId) + "-" + azKey.get(az[-1]) + "-epc" + epcKey.get(az[-1]) + "-own" + "-" + server_name_prefix + "-" + host_ip.replace(".", "-") + ".ximalaya.hw"
    print("hostname: ", new_host_name)
    return new_host_name


if __name__ == "__main__":
    metedata = _get_metedata()
    projectId = metedata.get("project_id")
    regionId = metedata.get("region_id")
    serverId = metedata.get("uuid")
    iam_url = "iam." + regionId + ".myhuaweicloud.com"
    bms_url = "bms." + regionId + ".myhuaweicloud.com"
    host_ip = _init_host_ip()
    new_host_name = _get_new_name()
    iam_token = _get_iam_token(projectId, iam_url)
#    hostname = _get_host_name()
#    serverId = _get_server_id(iam_token, bms_url, projectId, hostname)
    _change_server_name_in_bms(iam_token, bms_url, serverId, new_host_name, projectId)
    _change_local_hostname(new_host_name)