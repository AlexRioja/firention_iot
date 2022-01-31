#!/usr/bin/env python
import pickle
from time import sleep
import os
import paho.mqtt.client as mqttclient
import requests

bot_token = "5050407246:AAGAVbFGDw6zc60M43FFODhVhjK93i6T_PU"





def report(message,ID):
    bot_chatID = str(ID)
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + message

    response = requests.get(send_text)

    return response.json()


def on_connect(client,userdata,flags,rc):
    if rc == 0:
        print("CLIENT CONNECTED")
        global connected
        connected=True
    else:
        print("CLIENT NOT CONNECTED")

def on_message(client,userdata,message):
    msg = message.payload.decode('utf-8')
    msg_splitted = msg.split('$')
    slice1_splitted = msg_splitted[0].split(':')
    test_slice=slice1_splitted[1][1:]


    if test_slice == "*OnlineDataMissmatchAlarm*":
        for ID in ADMIN_CHAT_ID_LIST:
            slice2='\n'+msg_splitted[1]+'\n'
            slice3="\t\t\t"+msg_splitted[2]+'\n'
            slice4 = "\t\t\t" + msg_splitted[3] + '\n'
            slice5_splitted=msg_splitted[4].split("C*")
            slice5_1="\t\t\t"+slice5_splitted[0]+"C\n"
            slice5_2="\t\t\t*"+slice5_splitted[1][0:-2]
            toSend=test_slice+slice2+slice3+slice4+slice5_1+slice5_2
            report(toSend, ID)
    else:
        for ID in FIREFIGHTER_CHAT_ID_LIST:

            slice1= str(test_slice+":\n"+slice1_splitted[2]+":\n")
            slice2= str(msg_splitted[1]+'\n')
            slice3 = str("\t\t\t"+msg_splitted[2] + '\n')
            slice4 = str("\t\t\t" + msg_splitted[3] + '\n')
            slice5_splitted=msg_splitted[4].split("s*")
            slice5_1=str("\t\t\t" + slice5_splitted[0]+"s\n")
            slice5_2=str("\t\t\t*" +slice5_splitted[1]+'\n')
            slice6 = str("\t\t\t" + msg_splitted[5] + '\n')
            slice7_splitted=msg_splitted[6].split("\\t")
            slice7_1=str(slice7_splitted[0]+'\n')
            slice7_2=str("\t\t\t"+slice7_splitted[4][:-3]+'\n')
            slice7_3=str("\t\t\t"+slice7_splitted[8][:-5])
            toSend=slice1+slice2+slice3+slice4+slice5_1+slice5_2+slice6+slice7_1+slice7_2+slice7_3
            report(toSend, ID)

    print("MESSAGE RECEIVED")







if __name__ == '__main__':
    firstIteration = True
    while True:
        count=0

        if os.path.getsize("shared.pkl") > 0:
            with open("shared.pkl", "rb") as f:
                unpickler = pickle.Unpickler(f)
                # if file is not empty scores will be equal
                # to the value unpickled
                scores = unpickler.load()
                FIREFIGHTER_CHAT_ID_LIST = scores[0]
                ADMIN_CHAT_ID_LIST = scores[1]
                print(scores)






        if(firstIteration):
            firstIteration=False
            connected=False
            MessageReceived=False


            broker_address="broker.hivemq.com"
            port=1883
            scores = {}  # scores is an empty dict already
            client= mqttclient.Client("MQTT")
            client.on_connect=on_connect
            client.on_message = on_message
            client.connect(broker_address,port=port)
            client.loop_start()
            client.subscribe("ASP/telegram/firefighter")
            client.subscribe("ASP/telegram/admin")
            while connected!=True:
                sleep(0.2)
        while MessageReceived!=True and count<150:
            count+=1
            sleep(0.2)


