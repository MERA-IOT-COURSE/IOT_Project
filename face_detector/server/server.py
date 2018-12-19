#!/usr/bin/python3

import json

from paho.mqtt import client as mqtt
from server_logs import logger

INIT_TOPIC = "init_master"

topics = {}

MQTT_SERVER_HOST = "10.42.0.111"
MQTT_SERVER_PORT = 1883


def on_connect_callback(client, userdata, flags, rc):
    try:
        if rc:
            raise Exception("the device didn't connect to a server. Code: {}".format(rc))

        client.subscribe(INIT_TOPIC)
        logger.info("subscribed to the topic: {}".format(INIT_TOPIC))
    except Exception:
        logger.exception("an exception occured during a subscribe", exc_info = True)
        sys.exit(1)


def message_handler(client, msg_type, msg_body, topic):
    if msg_type == "REGISTER":
        cpu_serial = msg_body["hw_id"]
        topics[cpu_serial] = {
            "request": "dev_{}".format(cpu_serial),
            "response": "be_{}".format(cpu_serial)
        }

        try:
            if topic != INIT_TOPIC:
                raise Exception("Register message received from topic: {}".format(topic))
            client.subscribe(topics[cpu_serial]["request"])
            logger.info("subscribed to the topic: {}".format(topics[cpu_serial]["request"]))
            
            client.publish(topics[cpu_serial]["response"], json.dumps({
                "mid": "REGISTER_RESP",
                "data": {
                    "status": "OK"
                }
            }))
        except Exception as ex:
            client.publish(topics[cpu_serial]["response"], json.dumps({
                "mid": "REGISTER_RESP",
                "data": {
                    "status": "Can't register the device. {}".format(str(ex))
                }
            }))
    else:
        raise Exception("unkown message type found: {}".format(msg_type))


def on_message_callback(client, userdata, msg):
    payload = None
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
    except json.JSONDecodeError:
        logger.error("a json message with a payload '{}' can't be decoded. It was ignored".format(msg.payload.decode('utf-8')))
        return
    except Exception:
        logger.exception("an exception occured during a message decoding with a payload: {}".format(str(msg.payload)), exc_info = True)
    
    logger.info("a message was received from the topic: '{}' with a payload: {}".format(msg.topic, msg.payload))

    msg_type = None
    msg_body = None
    try:
        msg_type = payload["mid"]
        msg_body = payload["data"]
        message_handler(client, msg_type, msg_body, msg.topic)
    except KeyError:
        logger.exception("the message doesn't contain required keys. It was ignored", exc_info = True)
        return
    except Exception:
        logger.exception("an exception occured during message processing. It was ignored", exc_info = True)
        return


client = mqtt.Client()
client.on_connect = on_connect_callback
client.on_message = on_message_callback
client.connect(MQTT_SERVER_HOST, MQTT_SERVER_PORT, 60)

client.loop_forever()


# Connect to server
# Connect to DB
# Submit registration, save it to DB

# Make web part which works with the server (simple html)
