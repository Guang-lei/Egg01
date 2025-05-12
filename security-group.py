#!/usr/bin/env python


# SCRIPT_UUID = SC2024052015272701f4ca09f

import json
import os
import socket
import subprocess
import sys
import uuid
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


def _get_iam_token(projectId,iam_url):
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
        print("get token error: ", resp.status_code)
        sys.exit(1)


def _get_port_id(token, vpc_url, project_id, server_id, securityId):
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    url = "https://{vpc_url}/v1/{project_id}/ports?device_id={server_id}".format(
        vpc_url=vpc_url, project_id=project_id,server_id=server_id)
    resp = _common_http_request(url=url, method=METHOD_GET, headers=headers)
    if int(resp.status_code) == 200:
        result = json.loads(resp.content)
        print("port: ", result)
        for i in range(0, len(result["ports"])):
            port_id = result["ports"][i]["id"].encode('utf-8')
            if result["ports"][i]["fixed_ips"]:
                _add_securitygroup(iam_token, vpc_url, project_id, port_id, securityId)
    else:
        print("get port error: ", resp.status_code)
        sys.exit(1)


def _get_server_id(token, bms_url, project_id, hostname):
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    url = "https://{bms_url}/v1/{project_id}/baremetalservers/detail?name={hostname}".format(
        bms_url=bms_url, project_id=project_id, hostname=hostname)
    print("bmsurl: ", url)
    resp = _common_http_request(url=url, method=METHOD_GET, headers=headers)
    if int(resp.status_code) == 200:
        result = json.loads(resp.content)
        print("server_id:", result["servers"][0]["id"].encode('utf-8'))
        return result["servers"][0]["id"].encode('utf-8')
    else:
        print("get serverid error: ", resp.status_code)
        sys.exit(1)


def _get_metedata():
    command = "curl http://169.254.169.254/openstack/latest/meta_data.json"
    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = result.communicate()
    result1 = json.loads(output)
    return result1


def _add_securitygroup(token, vpc_url, project_id, port_id, security_groups_id):
    body = {
      "port": {
        "security_groups": [
          security_groups_id
        ]
      }
    }
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    url = "https://{vpc_url}/v1/{project_id}/ports/{port_id}".format(
        vpc_url=vpc_url, project_id=project_id,port_id=port_id)
    print(url)
    resp = _common_http_request(url=url, method=METHOD_PUT, headers=headers,data=body)
    if int(resp.status_code) == 200:
        print("addsecuritygroup ok")
    else:
        print("error: ", resp.status_code)
        sys.exit(1)


if __name__ == "__main__":
    metedata = _get_metedata()
    projectId = metedata.get("project_id")
    regionId = metedata.get("region_id")
    serverId = metedata.get("uuid")
    iam_url = "iam."+regionId+".myhuaweicloud.com"
    bms_url = "bms."+regionId+".myhuaweicloud.com"
    vpc_url = "vpc."+regionId+".myhuaweicloud.com"
    iam_token = _get_iam_token(projectId, iam_url)
#    hostname = _get_host_name()
#    server_id = _get_server_id(iam_token, bms_url, projectId, hostname)
    securityId = os.getenv('security_groups_id')
    _get_port_id(iam_token, vpc_url, projectId, serverId, securityId)
    