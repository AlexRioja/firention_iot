from os import curdir
import ssl
from time import sleep
import json
import utils
from device_provision_improved import ProvisionClient as PC
import device_provision_improved as dev_prov_imp
import math
import numpy as np
import random
from tb_device_mqtt import ProvisionClient, TBDeviceMqttClient, TBPublishInfo

"""
We are going to imagine that the station that detects strange things coordinates are:
40.705257, -3.894895
and the basestation is on:
40.717419, -3.918600
"""

print("Executing drone routine!!!")



station_coord=[40.782023, -3.883828]
number=2


# def calculateDistance(x1, y1, x2, y2):
#     dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
#     return dist
def calculateCircunf(r,n=10):
    return [(math.cos(2*math.pi/n*x)*r,math.sin(2*math.pi/n*x)*r) for x in range(0,n+1)]

#1.Provision drone instance in ThingsBoard
provision_req_1={
    "deviceName": "Firention_Drone_"+str(number),
    "provisionDeviceKey": "6qc66koo2vds8gocfbjc",
    "provisionDeviceSecret": "6yr5povhmdvab8c81rrf"
    }

provision_client=PC("srv-iot.diatel.upm.es", port=8883, provision_request=provision_req_1, credentials="generated/drones/cred_drone_"+str(number))
provision_client.tls_set_context(ssl.create_default_context())
provision_client.provision()

# #2.Calculate distance drone-station, to see if is possible
# distance=calculateDistance(station_coord[0],station_coord[1],drone_station_coord[0],drone_station_coord[1])*100
# print("Drone distance to the station is : "+str(round(distance, 2))+" km.")
# if distance>drone_range:
#     print("Location out of range!!!")
#     """
#     Send error, out of range
#     """

#3.If possible, send the drone and communicate telemetry
telemetry_drone={
    "id":number,
    "drone_latitude":station_coord[0],
    "drone_longitude":station_coord[1],
    "drone_altitude":0,
    "drone_battery":100,
    "drone_flightMode":"Awaiting",
    "drone_isFireDetected":False
}

client = TBDeviceMqttClient("srv-iot.diatel.upm.es", port=8883, token=utils.read_cred("generated/drones/cred_drone_"+str(number)))
# Connect to ThingsBoard
client.connect(tls=True)
# Sending telemetry without checking the delivery status
client.send_telemetry(telemetry_drone) 
# Sending telemetry and checking the delivery status (QoS = 1 by default)
result = client.send_telemetry(telemetry_drone, 0)


latitudes=None
longitudes=None
"""
1.-Calculate midpoints between position and destination and go 1 by 1 travelling to the destination
"""
for radius in [0.015, 0.032]:
    print(radius)
    circunf_points=calculateCircunf(radius,15)

    latitudes=np.linspace(station_coord[0],station_coord[0]+circunf_points[0][0],5)
    longitudes=np.linspace(station_coord[1],station_coord[1]+circunf_points[0][1],5)
    print(latitudes)
    print(longitudes)
    for i in range(len(latitudes)): #Go to location
        telemetry_drone["drone_altitude"]=random.randint(100,1000)/10
        telemetry_drone["drone_latitude"]=latitudes[i]
        telemetry_drone["drone_longitude"]=longitudes[i]
        telemetry_drone["drone_battery"]=telemetry_drone["drone_battery"]-1
        telemetry_drone["drone_flightMode"]="GoingToLocation"
        result = client.send_telemetry(telemetry_drone, 0)
        #print(telemetry_drone)
        # get is a blocking call that awaits delivery status  
        sleep(1)
    """
    2.-Patrol the surrounding area of the substation that has detected strange values
    """
    telemetry_drone["flightMode"]="CheckingLocation"
    for i in range(1,len(circunf_points)):#Patrol location
        telemetry_drone["drone_altitude"]=random.randint(100,1000)/10
        telemetry_drone["drone_latitude"]=station_coord[0]+circunf_points[i][0]
        telemetry_drone["drone_longitude"]=station_coord[1]+circunf_points[i][1]
        telemetry_drone["drone_battery"]=telemetry_drone["drone_battery"]-1
        result = client.send_telemetry(telemetry_drone, 0)
        #print(telemetry_drone)

        # get is a blocking call that awaits delivery status  
        sleep(2)
"""
3.-Return to the drone station
"""
for i in range(len(latitudes)): #Go to location
    telemetry_drone["drone_altitude"]=random.randint(100,1000)/10
    telemetry_drone["drone_latitude"]=latitudes[len(latitudes)-1-i]
    telemetry_drone["drone_longitude"]=longitudes[len(latitudes)-1-i]
    telemetry_drone["drone_battery"]=telemetry_drone["drone_battery"]-1
    telemetry_drone["drone_flightMode"]="ReturningToBase"
    result = client.send_telemetry(telemetry_drone, 0)
    # get is a blocking call that awaits delivery status  
    sleep(1)
"""
4.-Reset drone when reaching station
"""

telemetry_drone={
    "id":number,
    "drone_latitude":station_coord[0],
    "drone_longitude":station_coord[1],
    "drone_altitude":0,
    "drone_battery":100,
    "drone_flightMode":"Awaiting",
    "drone_isFireDetected":False
}

if random.randint(0,10)>7:
    telemetry_drone['drone_isFireDetected']=True

result = client.send_telemetry(telemetry_drone, 1)
# get is a blocking call that awaits delivery status  
success = result.get() == TBPublishInfo.TB_ERR_SUCCESS

# Disconnect from ThingsBoard
client.disconnect()