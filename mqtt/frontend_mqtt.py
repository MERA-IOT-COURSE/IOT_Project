#!/usr/bin/python3

import sys
import json
import time
import argparse
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
WEBCAM_SENSOR_ID = "face_recogn_web"
WEBCAM_SENSOR_TYPE = "webcam"
INIT_TOPIC = "init_master"
REQUEST_TOPIC = "dev_{}".format(CPU_SERIAL)
RESPONSE_TOPIC = "be_{}".format(CPU_SERIAL)

SERVER_HOST = "10.42.0.10"
SERVER_PORT = 1883


# Flag "auto" defines automatic sending data to server
# Flag "request" defines a request from a server for data sending. It will be reset by client after send
# Flag "registered" defines a successful registration
FLAGS = {
    "auto": False,
    "request": False,
    "registered": False
}


def message_handler(msg_type, msg_body):
    if msg_type == "REGISTER_RESP":
        if msg_body["status"] != "OK":
            FLAGS["registered"] = True
        else:
            raise Exception("bad registration with the response message: {}".format(msg_body["status"]))
    else:
        raise Exception("unkown message type found: {}".format(msg_type)


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
                    "name": "Face recognizer service",
                    "hw_id": CPU_SERIAL,
                    "actions": [],
                    "sensors": [{
                        "id": WEBCAM_SENSOR_ID,
                        "type": WEBCAM_SENSOR_TYPE,
                        "actions": ["webcam.recognize", "webcam.enable_auto", "webcam.disable_auto"]
                    }]
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
        payload = json.dumps(json.loads(msg.payload.decode('utf-8')), sort_keys = True, indent = 4)
    except json.JSONDecodeError:
        logger.error("a json message with a payload '{}' can't be decoded. It was ignored".format(msg.payload.decode('utf-8')))
        return
    except Exception
        logger.exception("an exception occured during a message decoding with a payload: {}".format(str(msg.payload)), exc_info = True)

    logger.info("a message was received from the topic: '{}' with a payload: {}".format(msg.topic, msg.payload))

    if args.listen:
        return

    msg_type = None
    msg_body = None
    try:
        msg_type = payload["msg"]
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
    while not FLAGS["registered"]:
        time.delay(0.1)
        registration_timeout -= 0.1
        if registration_timeout < 0:
            logger.info("registration timeout. client is aborted")
            sys.exit(1)

    '''
    DUMMY_DATA = {
        "sensor_id": WEBCAM_SENSOR_ID,
        "value": "__null__",
        "ts": str(datetime.datetime.now())
    }

    client.publish(REQUEST_TOPIC, json.dumps(DUMMY_DATA))
    '''
    # TODO processing with opencv


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
