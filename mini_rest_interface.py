import json
import requests
import os
try:
    import config
    user=config.tb_user
    password=config.tb_pass
except:
    user=os.environ['tb_user']
    password=os.environ['tb_pass']

server="https://srv-iot.diatel.upm.es"




def get_token():
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    }   
    data = '{"username":"'+user+'", "password":"'+password+'"}'
    r = requests.post(server+"/api/auth/login", headers=headers, data=data)

    res=json.loads(r.text)
    return res['token']


def delete_device(devId):
    token=get_token()
    r = requests.delete(server+'/api/customer/device/'+devId, headers={'X-Authorization': token})
    if(r.status_code==400):
        print("Invalid device ID! Cannot delete device with id-->"+devId+". Message-->"+r.text)
    


