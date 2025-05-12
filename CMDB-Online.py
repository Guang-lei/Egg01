#!/usr/bin/env python
# coding=utf-8

# SCRIPT_UUID = SC202405201543370131c55a9

import json
import os
import subprocess
import sys
import requests
import base64

# global params
METHOD_GET = 'GET'
METHOD_POST = 'POST'
METHOD_DELETE = 'DELETE'
METHOD_PATCH = 'PATCH'
METHOD_PUT = 'PUT'
project_id = ''
server_name = ''
# inputs params
iam_domain_name = os.getenv('iam_domain_name')
iam_user_name = os.getenv('iam_user_name')
iam_user_password = os.getenv('iam_user_password')
iam_endpoint = os.getenv('iam_endpoint')
ecs_endpoint = os.getenv('ecs_endpoint')
authorization = base64.b64decode(os.getenv('authorization'))
xmly_endpoint = 'cmdb.pd.ximalaya.local'


def _common_http_request(url, method, headers=None, data=None):
    headers = {} if headers is None else headers
    try:
        if data is not None:
            data = json.dumps(data, ensure_ascii=False)
        resp = requests.request(method, url, data=data, headers=headers)
        return resp
    except Exception as ex:
        print("Execute error: ", str(ex))
        raise ex


def _get_iam_token(iam_project_id):
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
                    'id': iam_project_id
                }
            }
        }
    }
    headers = {'Content-Type': 'application/json'}
    url = "https://{iam_url}/v3/auth/tokens".format(iam_url=iam_endpoint)
    resp = _common_http_request(url=url, method=METHOD_POST, headers=headers, data=body)
    if int(resp.status_code) == 201:
        token = resp.headers['X-Subject-Token']
        return token
    else:
        print("error: ", resp.status_code)
        sys.exit(1)


def _get_server_name(token, server_id):
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    url = "https://{ecs_url}/v1/{project_id}/cloudservers/{server_id}".format(
        ecs_url=ecs_endpoint, project_id=project_id, server_id=server_id)
    resp = _common_http_request(url=url, method=METHOD_GET, headers=headers)
    if int(resp.status_code) == 200:
        result = json.loads(resp.content)
        print("server_name:", result["server"]["name"].encode('utf-8'))
        return result["server"]["name"].encode('utf-8')
    else:
        print("error: ", resp.status_code)
        sys.exit(1)


def _get_openstack_metadata():
    command = "curl http://169.254.169.254/openstack/latest/meta_data.json"
    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = result.communicate()
    response = json.loads(output)
    return response


def _putaway_ecs_in_cmdb(meta_data):
    body = [{
        'name': server_name,
        'dependency': [{
            'dtype': '机架',
            'dname': 'hwcloud-' + meta_data.get("availability_zone").encode('utf-8')
        }]
    }]
    print("putaway bms body:" + json.dumps(body, ensure_ascii=False))
    headers = {"Content-Type": "application/json", "Authorization": authorization}
    print("putaway bms headers:" + json.dumps(headers))
    url = "http://{xmly_endpoint}/cmdb-web/machineManage/provider/update/dependency".format(xmly_endpoint=xmly_endpoint)
    print("putaway bms url:" + json.dumps(url))
    resp = _common_http_request(url=url, method=METHOD_PUT, headers=headers, data=body)
    print("change ecs instance to cmdb api status_code: " + str(resp.status_code))
    if int(resp.status_code) == 200:
        print("putaway ecs instance to cmdb succeeded, server_name: ", server_name)
        print("putaway ecs instance to cmdb api response: " + str(resp.content))
    else:
        print("error: ", resp.status_code)
        sys.exit(1)


# http://{xmly}/cmdb-web/machineManage/provider/machineInfo?name={host_name}
def _get_machine_info_from_cmdb(metadata):
    url = "http://{xmly_endpoint}/cmdb-web/machineManage/provider/machineInfo?name={host_name}".format(
        xmly_endpoint=xmly_endpoint, host_name=server_name)
    resp = _common_http_request(url=url, method=METHOD_GET)
    if int(resp.status_code) == 200:
        result = json.loads(resp.content)
        if result["data"] == '':
            _putaway_ecs_in_cmdb(metadata)
        elif result["data"]["name"] != server_name:
            _putaway_ecs_in_cmdb(metadata)
    else:
        print("check the host {server_name} from cmdb failed, please check the cmdb server")
        print("error: ", resp.status_code)
        sys.exit(1)


def _change_machine_status_in_cmdb():
    body = {
        "机器": server_name,
        "机器状态": "使用中"
    }
    print("change machine body:" + json.dumps(body, ensure_ascii=False))
    headers = {"Content-Type": "application/json", "Authorization": authorization}
    print("change machine headers:" + json.dumps(headers))
    url = "http://{xmly_endpoint}/cmdb-web/machineManage/provider/update/attributes".format(xmly_endpoint=xmly_endpoint)
    print("change machine url:" + json.dumps(url))
    resp = _common_http_request(url=url, method=METHOD_POST, headers=headers, data=body)
    print("change ecs instance status to cmdb api status_code: " + str(resp.status_code))
    if int(resp.status_code) == 200:
        print("change ecs instance status to cmdb succeeded, server_name: ", server_name)
        print("change ecs instance status to cmdb api response: " + str(resp.content))
    else:
        print("error: ", resp.status_code)
        sys.exit(1)


if __name__ == "__main__":
    print("inputs: ", iam_domain_name, iam_user_name, iam_user_password, iam_endpoint, ecs_endpoint, authorization)
    # init params
    metadata = _get_openstack_metadata()
    project_id = metadata.get("project_id").encode('utf-8')
    server_id = metadata.get("uuid").encode('utf-8')
    iam_token = _get_iam_token(project_id)
    server_name = _get_server_name(iam_token, server_id)
    _putaway_ecs_in_cmdb(metadata)
    # check first and put ecs in cmdb
    #_get_machine_info_from_cmdb(metadata)
    # change machine status
    _change_machine_status_in_cmdb()
