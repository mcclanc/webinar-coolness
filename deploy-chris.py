import json
import requests
import time
import argparse
import urllib3
urllib3.disable_warnings()

api_url_base = 'https://api.mgmt.cloud.vmware.com'
headers = {'Content-Type': 'application/json'}
refresh_token = "aH5NoYaoDLwv6pNkMJhMmT2f4vqNM040xt71wCLJqsI6xg6gywUO0EJ2S8HV9Lgr"

def get_access_key():
    api_url = 'https://console.cloud.vmware.com/csp/gateway/am/api/auth/api-tokens/authorize?refresh_token={0}'.format(refresh_token)
    response = requests.post(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        key = json_data['access_token']
        return key
    else:
        print(response.status_code)

access_key = get_access_key()
headers1 = {'Content-Type': 'application/json',
           'Authorization': 'Bearer {0}'.format(access_key)}

def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []
    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr
    results = extract(obj, arr, key)
    return results

def get_wp_bp_id():
    api_url = '{0}/blueprint/api/blueprints'.format(api_url_base)
    response = requests.get(api_url, headers=headers1, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        bp_id = extract_values(json_data,'id')
        for x in bp_id:
            api_url2 = '{0}/blueprint/api/blueprints/{1}'.format(api_url_base,x)
            response2 = requests.get(api_url2, headers=headers1, verify=False)
            if response2.status_code == 200:
                json_data2 = json.loads(response2.content.decode('utf-8'))
                bp_name = json_data2 ['name']
                if bp_name == 'chris-machine':
                    return x
    else:
        return None

def deploy_wp_bp():
    bpid = get_wp_bp_id()
    api_url = '{0}/blueprint/api/blueprint-requests'.format(api_url_base)
    data =  {
              "blueprintId": bpid,
              "deploymentName": "chris-nginx",
              "description": "Deployed Machine with Nginxand Chris",
              "projectId": "4b71f05c-691a-408f-9d5d-87aa0ec70c58"
            }
    response = requests.post(api_url, headers=headers1, data=json.dumps(data), verify=False)
    if response.status_code == 202:
        print('Successfully Started Chris Deployment')
    else:
        return None

print('Starting Chris Deployment')
deploy_wp_bp()
