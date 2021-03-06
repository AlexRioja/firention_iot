"""
This file connects to the https://www.embalses.net web-page and performs web scrapping to query the values of the different lakes in Madrid.
It also creates new devices in ThingsBoard with the lake information.

Should be called periodically (1 or 2 per day) to refresh information about water capacity in the lakes.
"""
from os import curdir
import ssl
from tb_device_mqtt import ProvisionClient, TBDeviceMqttClient, TBPublishInfo
import json
from bs4 import BeautifulSoup
import requests
import utils
from device_provision_improved import ProvisionClient as PC
import device_provision_improved as dev_prov_imp
from tqdm import tqdm
lakes=[]

#1.Open File
with open("data/lakes.json") as file:
    json_lakes=json.load(file)

#2.Read contents
for lake in json_lakes['lakes']:
    lakes.append(utils.Lake(lake["name"], lake["latitude"],lake["longitude"],lake["link"]))

print("Collecting information about Lakes in Madrid...")
#3.Obtain more information through web-scrapping
for lake in tqdm(lakes):
    print("\tScrapping info about-->"+lake.name)
    page = requests.get(lake.link)
    lake_html=BeautifulSoup(page.content, "html.parser")
    try: #when real-time data is available
        #get the table
        info_table = lake_html.find_all("div", class_="SeccionCentral")[2].find("div", class_="SeccionCentral_Caja")
        rows = info_table.find_all("div", class_="FilaSeccion")
        #get the rows that we want (0 and 2)
        current_water_hm3=rows[0].find_all("div", class_="Resultado")[0].text
        current_water_percentage=rows[0].find_all("div", class_="Resultado")[1].text
        total_capacity_hm3=rows[2].find_all("div", class_="Resultado")[0].text

    except: #when real time data is not available
        #get the table
        info_table = lake_html.find_all("div", class_="SeccionCentral")[1].find("div", class_="SeccionCentral_Caja")
        rows = info_table.find_all("div", class_="FilaSeccion")
        #get the rows that we want (0 and 2)
        current_water_hm3=rows[0].find_all("div", class_="Resultado")[0].text
        current_water_percentage=rows[0].find_all("div", class_="Resultado")[1].text
        total_capacity_hm3=rows[2].find_all("div", class_="Resultado")[0].text

    lake.capacity=total_capacity_hm3
    lake.percentage=current_water_percentage
    lake.current_water=current_water_hm3

i=0

print("Updating new lakes values in ThingsBoard...")
for lake in tqdm(lakes):

    #1.Create a lake device on the ThingsBoard platforms, all belongs to Firention_Lakes_Heroku profile
    provision_req_1={
    "deviceName": "Firention_Lake_"+str(i),
    "provisionDeviceKey": "s9dvyunb5bgsqc0xi793",
    "provisionDeviceSecret": "1g0m49f26wvzpn9lzhwz"
    }
    provision_client=PC("srv-iot.diatel.upm.es", port=8883, provision_request=provision_req_1, credentials="generated/lakes/cred_"+str(i))
    provision_client.tls_set_context(ssl.create_default_context())
    provision_client.provision()  # Request provisioned data

    #2.Send telemetry of the lake
    telemetry_lake={
        "name":lake.name,
        "latitude":lake.latitude,
        "longitude":lake.longitude,
        "value":lake.current_water,
        "value_max":lake.capacity,
        "percentage":lake.percentage
    }

    client = TBDeviceMqttClient("srv-iot.diatel.upm.es", port=8883, token=utils.read_cred("generated/lakes/cred_"+str(i)))
    # Connect to ThingsBoard
    client.connect(tls=True)
    # Sending telemetry without checking the delivery status
    client.send_telemetry(telemetry_lake) 
    # Sending telemetry and checking the delivery status (QoS = 1 by default)
    result = client.send_telemetry(telemetry_lake)
    # get is a blocking call that awaits delivery status  
    success = result.get() == TBPublishInfo.TB_ERR_SUCCESS
    # Disconnect from ThingsBoard
    client.disconnect()
    
    i+=1

print("\nFinished!")

















"""
telemetry = {"temperature": 41.9}

client = TBDeviceMqttClient("srv-iot.diatel.upm.es", port=8883, token="lcErj5SmOXvXlTy6LeCV")
# Connect to ThingsBoard
client.connect(tls=True)
# Sending telemetry without checking the delivery status
client.send_telemetry(telemetry) 
# Sending telemetry and checking the delivery status (QoS = 1 by default)
result = client.send_telemetry(telemetry)
# get is a blocking call that awaits delivery status  
success = result.get() == TBPublishInfo.TB_ERR_SUCCESS
# Disconnect from ThingsBoard
client.disconnect()
"""