"""
This file connects to the nasa firms api to get information about fires detected with their VIIRS satellite and algorithm.
It also creates devices on ThingsBoard to represent the fires.

Should be called periodically to refresh information in thingsboard.
"""
import requests
import json
import csv
import numpy as np
from tb_device_mqtt import TBDeviceMqttClient
from tb_rest_client.rest_client_ce import *
from tb_rest_client.rest import ApiException
from device_provision_improved import ProvisionClient as PC
import device_provision_improved as dev_prov_imp
import utils
import ssl

def delete_thingsBoard_device_by_id(url, id):
    with RestClientCE(base_url=url) as rest_client:
        try:
            rest_client.delete_device(DeviceId('DEVICE', id))
        except ApiException as e:
            print("ERRROR WHILE DELETING DEVICE")




res=requests.get("https://firms.modaps.eosdis.nasa.gov/api/country/csv/e3c1944690c80836c73b5dc5eb43cb89/VIIRS_SNPP_NRT/ESP/1/")
print(res.text)

res_json=[]
csvR=csv.DictReader(res.text.split('\n'),delimiter=',')

for rows in csvR:
    fire_info={}
    fire_info['latitude']=float(rows['latitude'])
    fire_info['longitude']=float(rows['longitude'])
    fire_info['intensity_detected']=(((float(rows['bright_ti4'])-32)/1.8)+((float(rows['bright_ti5'])-32)/1.8))/2
    fire_info['radiative_power_mw']=float(rows['frp'])
    fire_info['date']=rows['acq_date']
    fire_info['time']=rows['acq_time']
    if rows['confidence']=='n':
        fire_info['confidence']='normal'
    elif rows['confidence']=='l':
        fire_info['confidence']='low'
    elif rows['confidence']=='h':
        fire_info['confidence']=='high'
    res_json.append(fire_info)
#print(res_json)

#saving the information
with open("generated/extra/nasa_fire_info.json", "w") as f:
    json.dump(res_json,f)

devices=None
#checking the last values to delete
with open('generated/extra/fire_nasa_devices.txt', 'r+') as f:
    lines = f.readlines()
    for line in lines:
        devices=line.split(',')
    if devices!=None:
        for device in devices:
            delete_thingsBoard_device_by_id("srv-iot.diatel.upm.es", device)

#Adding new ones
i=0

for res in res_json:
    provision_req_1={
    "deviceName": "Firention_NASA_Fire_"+str(i),
    "provisionDeviceKey": "ohwkv3n5x0uawcewiylc",
    "provisionDeviceSecret": "17ujubr1ycf7ofb6veq9"
    }
    provision_client=PC("srv-iot.diatel.upm.es", port=8883, provision_request=provision_req_1, credentials="generated/extra/cred_"+str(i))
    provision_client.tls_set_context(ssl.create_default_context())
    provision_client.provision()  # Request provisioned data
    client = TBDeviceMqttClient("srv-iot.diatel.upm.es", port=8883, token=utils.read_cred("generated/extra/cred_"+str(i)))
    # Connect to ThingsBoard
    client.connect(tls=True)

    client.send_attributes(res) 
    # Disconnect from ThingsBoard
    client.disconnect()
    i+=1
print("Finished!")