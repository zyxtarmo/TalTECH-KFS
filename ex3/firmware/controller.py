#!/usr/bin/python
# -*- coding:utf-8 -*-

import SH1106
import config
import traceback
import time
import uuid
import paho.mqtt.client as paho
from PIL import Image, ImageDraw, ImageFont

# create client-id if does not exist
def get_uuid():
    try:
        with open("client_config.py", "r") as f:
            pass
    except FileNotFoundError:
        with open("client_config.py", "w") as f:
            f.write("uuid = '%s'\n" % uuid.uuid4())
    finally:
        import client_config
        return client_config.uuid

client_id = get_uuid()

# broker
broker="10.8.0.1"
broker_pass = "parool"
broker_username = "iot_module"

try:
    disp = SH1106.SH1106()
    disp.Init()
    disp.clear()
except IOError as e:
    print(e)

# Define callback
def on_message(client, userdata, message):
    global disp
    disp.clear()
    image1 = Image.new('1', (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1)
    font10 = ImageFont.truetype('Font.ttf', 13)
    draw.text((0, 0), str(message.payload.decode("utf-8")), font = font10, fill = 0)
    disp.ShowImage(disp.getbuffer(image1))
    print("received message =", str(message.payload.decode("utf-8")))
    time.sleep(5)
    welcome_screen()

def welcome_screen():
    global disp
    disp.clear()
    image1 = Image.new('1', (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1)
    font10 = ImageFont.truetype('Font.ttf', 13)
    draw.text((0, 0), "Welcome to", font = font10, fill = 0)
    draw.text((0, 20), "Smart Aquarium", font = font10, fill = 0)
    disp.ShowImage(disp.getbuffer(image1))
    time.sleep(3)

# init mqtt
client = paho.Client(client_id)

# Bind function to callback
client.on_message = on_message

# Set username and password
client.username_pw_set(username = broker_username, password = broker_pass)

print("connecting to broker ", broker)
client.connect(broker)   # connect
client.loop_start()      # start loop to process received messages
print("subscribing to: akvaarium/%s" % client_id)
client.subscribe("akvaarium/%s" % client_id) #subscribe
welcome_screen()

# loop until exit with CTRL + C
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("exiting")
    client.disconnect() # disconnect
    client.loop_stop()  # stop loop
