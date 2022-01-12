import json
import requests

server="https://srv-iot.diatel.upm.es"
user="a.mruiz@upm.es"
password="TB_pass_2021"



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
    


