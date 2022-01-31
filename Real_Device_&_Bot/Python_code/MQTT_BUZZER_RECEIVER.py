#!/usr/bin/env python
import serial
import logging
import json
import paho.mqtt.client as mqttclient
from time import sleep

Settings = json.load(open("Settings.json"))
# ThingsBoard REST API URL
url = Settings['URL']
arduino = serial.Serial(Settings['SERIAL_PORT'], baudrate=9600, timeout=15.0)


def on_connect(client,userdata,flags,rc):
    if rc == 0:
        print("CLIENT CONNECTED")
        global connected
        connected=True
    else:
        print("CLIENT NOT CONNECTED")

def on_message(client,userdata,message):
    msg = message.payload.decode('utf-8')
    res = json.loads(msg)
    params=res['params']
    if (params['activate']== True):
        toSend="on"
        arduino.write(toSend.encode())
    print("MESSAGE RECEIVED")

if __name__ == '__main__':

    firstIteration = True
    while True:

        if(firstIteration):
            firstIteration=False
            connected=False
            MessageReceived=False
            port=1883
            user="Z5Ae9cZpQM5CHmicyREB"
            scores = {}  # scores is an empty dict already
            client= mqttclient.Client("MQTT")
            client.on_connect=on_connect
            client.on_message = on_message
            client.connect("broker.hivemq.com",port=port)
            client.loop_start()
            client.subscribe("ASP/buzzer/activate")
            while connected!=True:
                sleep(0.2)
        while MessageReceived!=True:
            sleep(0.2)
