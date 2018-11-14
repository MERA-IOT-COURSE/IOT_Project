#!/usr/bin/python3

import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print("Message was received from topic: {}".format(msg.topic))
    try:
        print(json.loads(msg.payload.decode('utf-8')))
    except:
        print(msg.payload.decode('utf-8'))

def on_connect(client, userdata, flags, rc):
    if rc:
        print("Bad connection. Code: {}".format(rc))
        raise Exception("Bad connection")

    client.subscribe("#")



client = mqtt.Client()
client.on_message = on_message
client.on_connect = on_connect
client.connect("10.42.0.10", 1883, 60)
client.loop_forever()

