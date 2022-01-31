"""from tb_device_mqtt import ProvisionClient, TBDeviceMqttClient, TBPublishInfo

def handler(msg):
    print(msg)

client = TBDeviceMqttClient("srv-iot.diatel.upm.es", port=8883, token="Z5Ae9cZpQM5CHmicyREB")
client.connect(tls=True)

client.set_server_side_rpc_request_handler(handler)
"""

import os
import time
import sys
import json
import random
import paho.mqtt.client as mqtt

# Thingsboard platform credentials
THINGSBOARD_HOST = 'srv-iot.diatel.upm.es'
ACCESS_TOKEN = 'Z5Ae9cZpQM5CHmicyREB'
request = {"method": "activate", "params": ""}

# MQTT on_connect callback function
def on_connect(client, userdata, flags, rc):
    print("rc code:", rc)
    client.subscribe('v1/devices/me/rpc/response/+')
    client.publish('v1/devices/me/rpc/request/1',json.dumps(request), 1)

# MQTT on_message caallback function
def on_message(client, userdata, msg):
    print('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))

# start the client instance
client = mqtt.Client()

# registering the callbacks
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(ACCESS_TOKEN)
client.tls_set()
client.tls_insecure_set(True)
client.connect(THINGSBOARD_HOST, 8883, 60)

try:
    client.loop_forever()

except KeyboardInterrupt:
    client.disconnect()