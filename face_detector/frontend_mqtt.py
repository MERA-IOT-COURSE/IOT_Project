#!/usr/bin/python3

'''
TODO:
    * Registration delay
    * To do: complete a registration
'''

import os
import cv2
import sys
import json
import time
import base64
import argparse
import datetime
import subprocess

from paho.mqtt import client as mqtt
from frontend_logs import logger

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--listen", action="store_true")
args = parser.parse_args()


def get_raspberry_serial():
    command = "grep -Po '^Serial\s*:\s*\K[[:xdigit:]]{16}' /proc/cpuinfo"
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    serial = p.stdout.read().decode('utf-8')[:-1]
    logger.info("raspberry serial defined as '{}'".format(serial))
    return serial


MQTT_PROTO_VERSION = "1.0"
CPU_SERIAL = get_raspberry_serial()
WEBCAM_SENSOR_ID = "recogn_webcam"
WEBCAM_SENSOR_TYPE = "sensor.webcam"
INIT_TOPIC = "init_master"
REQUEST_TOPIC = "dev_{}".format(CPU_SERIAL)
RESPONSE_TOPIC = "be_{}".format(CPU_SERIAL)

SERVER_HOST = "10.42.0.10"
SERVER_PORT = 1883

# Flag "auto" defines automatic sending data to server
# Flag "registered" defines a successful registration
FLAGS = {
    "auto": True,
    "registered": False
}

DEV_ACTIONS = [{
    "id": "custom.enable_auto_detection",
    "name": "Enable an automatic face detection"
}, {
    "id": "custom.disable_auto_detection",
    "name": "Disable an automatic face detection" 
}]

SENSORS = [{
    "id": WEBCAM_SENSOR_ID,
    "type": WEBCAM_SENSOR_TYPE,
    "actions": []
}]

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
CLASSIFIER_PATH = os.path.join(BASE_DIR, 'models', 'haarcascade_frontalface_default.xml')


logger.info("The device has been initialized. Loading the face cascade classifier..")
classifier = cv2.CascadeClassifier(CLASSIFIER_PATH)
logger.info("Face cascade classfifier has been loaded")


def message_handler(msg_type, msg_body):
    if msg_type == "REGISTER_RESP":
        if msg_body["status"] != "OK":
            FLAGS["registered"] = True
        else:
            raise Exception("bad registration with the response message: {}".format(msg_body["status"]))
    elif msg_type == "REQ_DEVICE_ACTION":
        if msg_body["id"] == "custom.enable_auto_detection":
            FLAGS["auto"] = True
        elif msg_body["id"] == "custom.disable_auto_detection":
            FLAGS["auto"] = False
        else:
            message = "Unknown action id was received for device"
            client.publish(REQUEST_TOPIC, json.dumps({
                "id": msg_body["id"],
                "status": "error",
                "data": message
            }))
            raise Exception(message)

        client.publish(REQUEST_TOPIC, json.dumps({
            "id": msg_body["id"],
            "status": "success",
            "data": ""
        }))
    else:
        raise Exception("unkown message type found: {}".format(msg_type))


def on_connect_callback(client, userdata, flags, rc):
    try:
        if rc:
            raise Exception("the device didn't connect to a server. Code: {}".format(rc))

        if args.listen:
            client.subscribe('#')
        else:
            # There is a body for a client registration
            register_body = {
                "mid": "REGISTER",
                "data": {
                    "version": MQTT_PROTO_VERSION,
                    "name": "Face detector service",
                    "hw_id": CPU_SERIAL,
                    "actions": DEV_ACTIONS,
                    "sensors": SENSORS
                }
            }

            client.publish(INIT_TOPIC, json.dumps(register_body))
            client.subscribe(RESPONSE_TOPIC)
    except Exception:
        logger.exception("an exception occured during a connection", exc_info = True)
        sys.exit(1)


def on_message_callback(client, userdata, msg):
    payload = None
    try:
        # We try to get pretty json
        payload = json.loads(msg.payload.decode('utf-8'))
    except json.JSONDecodeError:
        logger.error("a json message with a payload '{}' can't be decoded. It was ignored".format(msg.payload.decode('utf-8')))
        return
    except Exception:
        logger.exception("an exception occured during a message decoding with a payload: {}".format(str(msg.payload)), exc_info = True)

    logger.info("a message was received from the topic: '{}' with a payload: {}".format(msg.topic, msg.payload))

    if args.listen:
        return

    msg_type = None
    msg_body = None
    try:
        
        msg_type = payload["mid"]
        msg_body = payload["data"]
        message_handler(msg_type, msg_body)
    except KeyError:
        logger.exception("the message doesn't contain required keys. It was ignored", exc_info = True)
        return
    except Exception:
        logger.exception("an exception occured during message processing. It was ignored", exc_info = True)
        return


def main_thread(client):
    registration_timeout = 5
    while False:
        time.sleep(0.1)
        registration_timeout -= 0.1
        if registration_timeout < 0:
            logger.info("registration timeout. client is aborted")
            sys.exit(1)

    capture = cv2.VideoCapture(0)
    while True:
        ret, frame = capture.read()
        if not ret:
            logger.warning("frame capturing error")
            continue

        if not FLAGS["auto"]:
            time.sleep(0.5)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = classifier.detectMultiScale(
            gray,
            scaleFactor = 1.2,
            minNeighbors = 6,
            minSize = (75, 75)
        )

        cropped_faces = []
        for face in faces:
            (xtl, ytl, width, height) = face
            crop = frame[ytl:ytl + height, xtl:xtl + width]
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
            result, encimg = cv2.imencode('.jpg', crop, encode_param)
            if not result:
                logging.warning("jpeg encoding error")

            cropped_faces.append(base64.b64encode(encimg.tobytes()).decode('utf-8'))

        if len(cropped_faces):
            client.publish(REQUEST_TOPIC, json.dumps({
                "mid": "SENSOR_DATA",
                "data": {
                    "sensor_id": WEBCAM_SENSOR_ID,
                    "value": cropped_faces,
                    "ts": str(datetime.datetime.now())
                }
            }))
            time.sleep(2)             

client = mqtt.Client()

if args.listen:
    logger.info('the client is running in a listen mode')
else:
    logger.info('the client is running in a publish mode')

client.on_connect = on_connect_callback
client.on_message = on_message_callback
client.connect(SERVER_HOST, SERVER_PORT, 60)

if args.listen:
    client.loop_forever()
else:
    client.loop_start()
    main_thread(client)
    client.loop_stop()
