import requests
import json
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning

def delete_snapshots():
    global rhev_namelist
    global api_user
    global api_password

    api_user='admin@internal'
    api_password='**************'
 
    rhev_namelist = [
        "rhevmananager.yourcompany.local", #put your rhev managers list here
        ]

    for rhev_name in rhev_namelist:
        auth = '/ovirt-engine/sso/oauth/token'
        vm_path = '/ovirt-engine/api/vms'

        payload = {
            'grant_type': 'password',
            'scope': 'ovirt-app-api',
            'username': api_user,
            'password': api_password
        }
        temp_header = {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json'
        }
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        session = requests.post("https://"+rhev_name+auth, headers=temp_header, verify=False, data=payload)
        session_id = session.json()
        token = session_id["access_token"]

        auth_header = {
        'Accept': 'application/json',
        'Authorization': 'Bearer '+ token
        }

        vm_list = requests.get("https://"+rhev_name+vm_path, headers = auth_header, verify=False)
        rhev_vmlist = vm_list.json()

        for vmlist in rhev_vmlist["vm"]:
            vm_id = vmlist["id"]
            snaphost_list_path = "/ovirt-engine/api/vms/"+vm_id+"/snapshots"
            snapshot_list = requests.get("https://"+rhev_name+snaphost_list_path, headers = auth_header, verify=False)
            rhev_snaplist = snapshot_list.json()
            for snap in rhev_snaplist["snapshot"]:
                snapshot_type = snap.get("snapshot_type")
                snapshot_age = (time.time()-snap["date"]/1000) / 3600 #snapshot time calculations
                if snapshot_type == "regular" and snapshot_age > 500: #snapshot age more than 500 hours
                    # print(snap["description"], snap["id"], snapshot_age)
                    snap_id = snap["id"]
                    snapshot_delete_path = "/ovirt-engine/api/vms/"+vm_id+"/snapshots/"+snap_id
                    delete_snapshot = requests.delete("https://"+rhev_name+snapshot_delete_path, headers = auth_header, verify=False)
                    print(delete_snapshot)

delete_snapshots()
