import serial
import logging
import json
import random
# Importing models and REST client class from Community Edition version
from tb_rest_client.rest_client_ce import *
# Importing the API exception
from tb_rest_client.rest import ApiException


def createasset(nameIN, typeIN):
    asset = Asset(name=nameIN, type=typeIN)
    asset = rest_client.save_asset(asset)

    logging.info("Asset was created:\n%r\n", asset)
    return asset


def createdevice(specs):
    device = Device(name=specs['name'], type=specs['type'])
    device = rest_client.save_device(device)

    logging.info(f'{specs["name"]} was created:\n{device}\n')
    return device


def createrelation(assetIN, deviceIN, typeRelation):
    # Creating relations from device to asset
    relation = EntityRelation(
        _from=assetIN.id,
        to=deviceIN.id,
        type=typeRelation)
    relation = rest_client.save_relation(relation)

    logging.info(" Relation 1 was created:\n%r\n", relation)


def smokeGenerator(isFire, smoke):
    fire_possibility = (random.randint(0, 100) > 85)
    calm_possibility = (random.randint(0, 100) > 75)
    increment = 0

    if (isFire):
        increment = random.randint(-10, 90) / 10
        if (calm_possibility):
            # EXIT FROM FIRE STATUS
            isFire = False
            increment = random.randint(-80, 10) / 10

    else:
        increment = random.randint(-100, 10) / 10
        if (fire_possibility):
            #we ENTER the fire
            isFire = True
            increment = random.randint(-10, 80) / 10

    smoke = smoke + increment
    if (smoke < 0):
        smoke = 0
    if (smoke > 100):
        smoke = 100

    return isFire, smoke

def windGenerator(anem,wdir):
    anem=anem+random.randint(-27, 30)/10
    wdir=wdir+random.randint(-28, 30)/10
    if(anem < 0):
        anem=0
    if(anem > 32.4):
        anem=32.4
    if(wdir < 0):
        wdir=0
    if(wdir > 359):
        wdir=359

    wdir = round(wdir,1)
    anem = round(anem)
    return anem,wdir

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    firstSmokeSampling=True
    isFire = False
    smoke = 0
    firstWindSampling = True
    anem = 0
    wdir = 0


    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    Settings = json.load(open("Settings.json"))
    # ThingsBoard REST API URL
    url = Settings['URL']
    # Default Tenant Administrator credentials
    username = Settings['USERNAME']
    password = Settings['PASSWORD']
    encoding = Settings['ENCODING']
    station_name = Settings['STATION_NAME']

    for i, c in enumerate(station_name):
        if c.isdigit():
            firstDigit = i
            break
    station_number = station_name[firstDigit:]
    for i, c in enumerate(station_number):
        if not (c == '0'):
            firstDigit = i
            break
    TemperatureSensorName = "Firention_Temperature_" + station_number
    SmokeSensorName = "Firention_Smoke_" + station_number
    AnemometerSensorName = "Firention_Anemometer_" + station_number
    DroneName = "Firention_Drone_" + station_number[firstDigit:]
    OnlineWeatherName = "OnlineWeather" + station_number
    BuzzerName="Firention_buzzer_"+station_number
    PIRName="Firention_PIR_"+station_number

    deviceSpecs = [{"name": TemperatureSensorName,
                    "type": "Firention_temp_profile",
                    "relation": "Contains"},
                   {"name": SmokeSensorName,
                    "type": "Firention_smoke_profile",
                    "relation": "Contains"},
                   {"name": AnemometerSensorName,
                    "type": "Firention_Anemometer_profile",
                    "relation": "Contains"},
                   {"name": DroneName,
                    "type": "Firention_Drone_profile",
                    "relation": "HasDrone"},
                   {"name": OnlineWeatherName,
                    "type": "Firention_OpenWeatherOnline_data",
                    "relation": "HasOnlineData"},
                   {"name": BuzzerName,
                    "type": "Firention_buzzer",
                    "relation": "HasBuzzer"},
                   {"name": PIRName,
                    "type": "Firention_PIR_profile",
                    "relation": "Contains"}

                   ]

    devicesList = []
    checkList = [0] * 20
    checkCount = 0
    terminatingCondition = 2 * (1 + len(deviceSpecs)) - 1

    arduino = serial.Serial(Settings['SERIAL_PORT'], baudrate=9600, timeout=15.0)
    fixCondition = False

    while not fixCondition:
        line = arduino.readline()
        line = line.decode(encoding)
        line = line.rstrip()
        line_splitted = line.split(',')
        if (len(line_splitted) > 3):
            latitude = float(line_splitted[2])
            longitude = float(line_splitted[3])
            asset_attribute = f'{"{"}"latitude":{latitude:.2f}, "longitude":{longitude:.2f}{"}"}'
            fixCondition = True

    with RestClientCE(base_url=url) as rest_client:
        while checkCount < terminatingCondition:
            try:
                # Auth with credentials
                rest_client.login(username=username, password=password)
                if checkList[0] == 0:
                    findAsset = rest_client.get_tenant_asset(station_name)
                    AssetToDelete = findAsset.id
                    rest_client.delete_asset(AssetToDelete.id)
                    logging.info(" OLD ASSET DELETED\n")
                    checkList[0] += 1
                    checkCount += 1

                if checkCount > 1:
                    checkCount = 1
                for dev in deviceSpecs:
                    if checkList[checkCount] == 0:
                        tmp = dev['name']

                        findDevice = rest_client.get_tenant_device(tmp)
                        deviceToDelete = findDevice.id
                        rest_client.delete_device(deviceToDelete.id)
                        logging.info(f'{dev["name"]} DELETED\n')
                        checkList[checkCount] += 1
                    checkCount += 1

                if checkCount > len(deviceSpecs) + 1:
                    checkCount = len(deviceSpecs) + 1

                if checkList[checkCount] == 0:
                    # Creating an Asset
                    asset = createasset(
                        nameIN=station_name, typeIN="SubStation")

                    # Asset attribute
                    asset_attribute_json = json.loads(asset_attribute)
                    res = rest_client.save_entity_attributes_v2(
                        body=asset_attribute_json, entity_type='ASSET', entity_id=EntityId(
                            'ASSET', asset.id), scope='SERVER_SCOPE')
                    checkList[checkCount] += 1
                    checkCount += 1

                if checkCount > len(deviceSpecs) + 2:
                    checkCount = len(deviceSpecs) + 2

                # creating Devices

                for specs in deviceSpecs:
                    if checkList[checkCount] == 0:
                        device_tmp = createdevice(specs)
                        devicesList.append(device_tmp)
                        createrelation(asset, device_tmp, specs['relation'])
                        checkList[checkCount] += 1
                    checkCount += 1

            except ApiException as e:

                logging.exception(e)
                checkList[checkCount] += 1
                checkCount += 1
                continue

        while True:
            line = arduino.readline()
            line = line.decode(encoding)
            line = line.rstrip()
            line_splitted = line.split(',')
            if not (len(line_splitted) > 3):
                humidity = float(line_splitted[0])
                temperature = float(line_splitted[1])
                movementDetected = float(line_splitted[2])
                if (firstSmokeSampling):
                    smoke = random.randint(0, 10)
                    isFire = (random.uniform(0, 1) > 0.5)
                    isFire, smoke = smokeGenerator(isFire, smoke)
                else:
                    isFire, smoke = smokeGenerator(isFire, smoke)
                if (firstWindSampling):
                    anem = random.randint(0, 324) / 10
                    wdir = random.randint(0, 360)
                    anem, wdir = windGenerator(anem, wdir)

                else:
                    anem, wdir = windGenerator(anem, wdir)

                body = f'{"{"}"humidity":{humidity:.2f}, "temperature":{temperature:.2f}{"}"}'
                body_json = json.loads(body)
                rest_client.save_entity_telemetry(entity_type='DEVICE', entity_id=EntityId(
                    'DEVICE', devicesList[0].id), scope='SERVER_SCOPE', body=body_json)
                logging.info("TEMP/HUM Telemetry SENT!\n")


                body = f'{"{"}"smoke":{smoke:.2f}{"}"}'
                body_json = json.loads(body)
                rest_client.save_entity_telemetry(entity_type='DEVICE', entity_id=EntityId(
                    'DEVICE', devicesList[1].id), scope='SERVER_SCOPE', body=body_json)
                logging.info("SMOKE Telemetry SENT!\n")


                body = f'{"{"}"anem_data":{anem:.1f}, "wind_direction":{wdir:.0f}{"}"}'
                body_json = json.loads(body)
                rest_client.save_entity_telemetry(entity_type='DEVICE', entity_id=EntityId(
                    'DEVICE', devicesList[2].id), scope='SERVER_SCOPE', body=body_json)
                logging.info("WIND Telemetry SENT!\n")

                if (movementDetected>0):
                    move="true"
                else:
                    move = "false"

                body = f'{"{"}"isMovementDetected":"{move}"{"}"}'
                body_json = json.loads(body)
                rest_client.save_entity_telemetry(entity_type='DEVICE', entity_id=EntityId(
                    'DEVICE', devicesList[6].id), scope='SERVER_SCOPE', body=body_json)
                logging.info("MOVE Telemetry SENT!\n")


