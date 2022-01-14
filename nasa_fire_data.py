"""
This file connects to the nasa firms api to get information about fires detected with their VIIRS satellite and algorithm.
It also creates devices on ThingsBoard to represent the fires.

Should be called periodically to refresh information in thingsboard.
"""
import requests
import json
import csv
from tb_device_mqtt import TBDeviceMqttClient

from device_provision_improved import ProvisionClient as PC
import utils
import ssl
import glob 
import mini_rest_interface as tb_rest
from tqdm import tqdm
import config

print("Collecting information about NASA VIIRS detected fires in Spain...")
res=requests.get("https://firms.modaps.eosdis.nasa.gov/api/country/csv/"+config.nasa_api_key+"/VIIRS_SNPP_NRT/ESP/1/")
print("\n\t--------------------INFORMATION RETRIEVED-------------------\n"+res.text)
print("\t--------------------END OF INFORMATION RETRIEVED-------------------\n")

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

print("Deleting previous fires in ThingsBoard...")
#Deleting previous devices from control files
for cred_file in tqdm(glob.glob('generated/extra/cred_*')):
    new_credentials=None
    try:
        with open(cred_file, "r") as credentials_file:
            new_credentials = credentials_file.read()
    except Exception as e:
        #print("Get Credentials:"+str(e))
        pass
    tb_rest.delete_device(new_credentials)

#Adding new ones
i=0
print("Updating with the new fires in ThingsBoard...")
for res in tqdm(res_json):
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
print("\nFinished!")