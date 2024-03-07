#!/usr/bin/python
# -*- coding:utf-8 -*-

import SH1106
import config
import traceback
import time
import paho.mqtt.client as paho
from PIL import Image, ImageDraw, ImageFont


broker="10.8.0.1"

# Define callback
def on_message(client, userdata, message):
    print("received message =", str(message.payload.decode("utf-8")))
    time.sleep(5)

client = paho.Client("client-NN") 

# Bind function to callback
client.on_message = on_message

# Set username and password
client.username_pw_set(username = "iot_module", password = "parool")

print("connecting to broker ", broker)
client.connect(broker)   # connect
client.loop_start()      # start loop to process received messages
print("subscribing ")
client.subscribe("class/iotNN") #subscribe
time.sleep(2)

# loop until exit with CTRL + C
try:
        while True:
                    time.sleep(1)

except KeyboardInterrupt:
    print("exiting")
    client.disconnect() # disconnect
    client.loop_stop()  # stop loop
