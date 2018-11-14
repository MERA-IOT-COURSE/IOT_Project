#!/usr/bin/python

import json
import time
import subprocess
import datetime
import paho.mqtt.client as mqtt

def get_serial():
    command = "grep -Po '^Serial\s*:\s*\K[[:xdigit:]]{16}' /proc/cpuinfo"
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    return p.stdout.read().decode('utf-8')[:-1]

MQTT_PROTO_VERSION = "1.0"
CPU_SERIAL = get_serial()
WEBCAM_SENSOR_ID = "face_recogn_web"
WEBCAM_SENSOR_TYPE = "webcam"
INIT_TOPIC = "init_master"
REQUEST_TOPIC = "dev_{}".format(CPU_SERIAL)
RESPONSE_TOPIC = "be_{}".format(CPU_SERIAL)

def on_connect(client, userdata, flags, rc):
    if rc:
        print("Bad connection. Code: {}".format(rc))
        raise Exception("Bad connection")

    registration_data = {
        "version": MQTT_PROTO_VERSION,
        "name": "Face recognizer service",
        "hw_id": CPU_SERIAL,
        "actions": [],
        "sensors": [{
            "id": WEBCAM_SENSOR_ID,
            "type": WEBCAM_SENSOR_TYPE,
            "actions": ["webcam.recognize", "webcam.enable_auto", "webcam.disable_auto"]
        }]
    }

    client.publish(INIT_TOPIC, json.dumps(registration_data))
    client.subscribe(RESPONSE_TOPIC)


def on_message(client, userdata, msg):
    print(msg.topic + ": " + str(msg.payload))


def main_thread(client):
    time.sleep(2)

    DUMMY_DATA = {
        "sensor_id": WEBCAM_SENSOR_ID,
        "value": "__null__",
        "ts": str(datetime.datetime.now())
    }

    client.publish(REQUEST_TOPIC, json.dumps(DUMMY_DATA))
    time.sleep(2)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("10.42.0.10", 1883, 60)

client.loop_start()
main_thread(client)
client.loop_stop()
