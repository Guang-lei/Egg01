#!/usr/bin/env python

# SCRIPT_UUID = SC202405161929320131b5256

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
host_ip = ''
# inputs params
#project_id = os.getenv('project_id')
iam_domain_name = os.getenv('iam_domain_name')
iam_user_name = os.getenv('iam_user_name')
iam_user_password = os.getenv('iam_user_password')
iam_url = os.getenv('iam_endpoint')
ecs_url = os.getenv('ecs_endpoint')
server_name_prefix = os.getenv('server_name_prefix')
#new_host_name = server_name_prefix + '-' + uuid.uuid4().hex[:6]


def _init_host_ip():
    host_name = socket.getfqdn(socket.gethostname())
    ip = socket.gethostbyname(host_name)
    return ip


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


def _get_iam_token(projectId):
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
        print("error: ", resp.status_code)
        sys.exit(1)




def _change_server_name_in_ecs(token, ecs_server_id,new_host_name,project_id):
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    url = "https://{ecs_url}/v2.1/{project_id}/servers/{server_id}".format(
        ecs_url=ecs_url, project_id=project_id, server_id=ecs_server_id)
    # name: prefix + 6bit uuid
    body = {
        "server": {
            "name": new_host_name
        }
    }
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
    metedata=_get_metedata()
    regionId=metedata.get("region_id")
    regionKey={"cn-east-3":"sh1","cn-north-4":"bj1"}
    az=metedata.get("availability_zone")
    chargingMode=metedata.get("meta",{}).get("charging_mode")
    azKey={"a":"1","b":"2","c":"3","d":"4"}
    chargingKey={"0":"usage","1":"month"}
    print("ip: ", host_ip)
    new_host_name=regionKey.get(regionId)+"-"+azKey.get(az[-1])+"-cloud-"+chargingKey.get(chargingMode)+"-"+server_name_prefix+"-"+host_ip.replace(".","-")+".ximalaya.hw"
    return new_host_name

if __name__ == "__main__":
    host_ip = _init_host_ip()
    new_host_name=_get_new_name()
    metedata=_get_metedata()
    projectId=metedata.get("project_id")
    iam_token = _get_iam_token(projectId)
    print(iam_token)
    server_id=metedata.get("uuid")
    _change_server_name_in_ecs(iam_token, server_id,new_host_name,projectId)
    _change_local_hostname(new_host_name)
