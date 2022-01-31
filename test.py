from tb_device_mqtt import ProvisionClient, TBDeviceMqttClient, TBPublishInfo

telemetry_drone={
    "temperature":-50,
    "humidity":0,
    "description":"test description",
    "rain":"false"
}

client = TBDeviceMqttClient("srv-iot.diatel.upm.es", port=8883, token="khU5r4KJczyo1CixbO0i")
# Connect to ThingsBoard
client.connect(tls=True)
# Sending telemetry without checking the delivery status
print(client.send_telemetry(telemetry_drone).get()) 

"""
devices=["khU5r4KJczyo1CixbO0i","ebAXCKsRBrGnZpWaxmq4","hPujheyhNGutLIIltee4","ebAGlqUNoBAgPpS1T7Rl","KOfWLGDPduxeBUp4ewxR"]
locations=[""]

def get_online_data():
    request_link = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={Settings["API_KEY"]}&exclude={Settings["EXCLUDE"]}&units={Settings["UNITS"]}&lang={Settings["LANG"]}'
    print(request_link)
    r = requests.get(request_link)
    body = json.dumps(r.json(), indent=4)
    responseDict = json.loads(body)
    print(responseDict)

    currentDict = responseDict['current']
    temp = currentDict['temp']
    humidity = currentDict['humidity']
    weather = currentDict['weather']
    weather = weather[0]
    weatherDescription = weather['description']
    if (weather['main'] != "Undefined"):
        if (weather['main'] == "Rain"):
            rainFlag="true"

    tmp = dict(description=weatherDescription,humidity=humidity,temperature=temp,rain=rainFlag)
    tmp=f'{"{"}"humidity":{humidity},"description":\"{weatherDescription}\","rain":\"{rainFlag}\", "temperature":{temp:.2f}{"}"}'
    toSend_json = json.loads(tmp)


for devToken in devices:
    telemetry={
    "temperature":-50,
    "humidity":0,
    "description":"test description",
    "rain":"false"
    }

    client = TBDeviceMqttClient("srv-iot.diatel.upm.es", port=8883, token=devToken)
    # Connect to ThingsBoard
    client.connect(tls=True)
    # Sending telemetry without checking the delivery status
    print(client.send_telemetry(telemetry_drone).get()) 



import requests
import json
import logging
from time import sleep

# Importing models and REST client class from Community Edition version
from tb_rest_client.rest_client_ce import *
# Importing the API exception
from tb_rest_client.rest import ApiException

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    Settings = json.load(open("Settings_weather.json"))
    assetsList=[]
    # ThingsBoard REST API URL
    url = Settings['URL']
    # Default Tenant Administrator credentials
    username = Settings['USERNAME']
    password = Settings['PASSWORD']
    stationNumber = Settings['STATION_NUMBER']
    with RestClientCE(base_url=url) as rest_client:
        rest_client.login(username=username, password=password)
        for i in range(1,Settings['STATION_NUMBER']+1):
            name=str("SubStation00"+str(i))
            findAsset = rest_client.get_tenant_asset(name)
            AssetToSave = findAsset.id
            assetsList.append({'ID':AssetToSave.id})

        while True:
            for i,asset in enumerate(assetsList):
                rainFlag = "false"
                lat_DICT =  rest_client.get_attributes(entity_type = 'ASSET', entity_id = EntityId('ASSET', asset['ID']),keys='latitude')
                lon_DICT = rest_client.get_attributes(entity_type='ASSET', entity_id=EntityId('ASSET', asset['ID']),keys='longitude')
                lat=lat_DICT[0]['value']
                lon= lon_DICT[0]['value']
                request_link = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={Settings["API_KEY"]}&exclude={Settings["EXCLUDE"]}&units={Settings["UNITS"]}&lang={Settings["LANG"]}'
                print(request_link)
                r = requests.get(request_link)
                body = json.dumps(r.json(), indent=4)
                responseDict = json.loads(body)
                print(responseDict)

                currentDict = responseDict['current']
                temp = currentDict['temp']
                humidity = currentDict['humidity']
                weather = currentDict['weather']
                weather = weather[0]
                weatherDescription = weather['description']
                if (weather['main'] != "Undefined"):
                    if (weather['main'] == "Rain"):
                        rainFlag="true"

                tmp = dict(description=weatherDescription,humidity=humidity,temperature=temp,rain=rainFlag)
                tmp=f'{"{"}"humidity":{humidity},"description":\"{weatherDescription}\","rain":\"{rainFlag}\", "temperature":{temp:.2f}{"}"}'
                toSend_json = json.loads(tmp)
                name = str("OnlineWeather00" + str(i+1))
                findDevice = rest_client.get_tenant_device(name)
                deviceFound = findDevice.id
                tmp=deviceFound.id

                rest_client.save_entity_telemetry(entity_type='DEVICE', entity_id=EntityId(
                    'DEVICE', tmp), scope='SERVER_SCOPE', body=toSend_json)
                logging.info("Telemetry SENT!\n")

            logging.info("########## SLEEP BEGIN ##############\n")
            sleep(60)
            logging.info("########## SLEEP END ##############\n")





"""