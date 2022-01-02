from os import curdir
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
import json
from bs4 import BeautifulSoup
import requests
import utils

lakes=[]

#1.Open File
with open("lakes.json") as file:
    json_lakes=json.load(file)

#2.Read contents
for lake in json_lakes['lakes']:
    lakes.append(utils.Lake(lake["name"], lake["latitude"],lake["longitude"],lake["link"]))

#3.Obtain more information through web-scrapping
for lake in lakes:
    print("Scrapping info about-->"+lake.name)
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