import json
import random
from time import sleep

import paho.mqtt.client as mqtt

# Flags
flags = [False, False, False]

POSITION_UPDATE = 0
COMMAND_UPDATE = 1
STATUS_UPDATE = 2

bunsen_position = []
bunsen_gripper_status = ""
bunsen_command = ""


def on_connect(client, user_data, flags, rc):
    print("Connected with result code " + str(rc))

    client.subscribe("Bunsen/#")


def on_message(client, user_data, msg):
    global bunsen_position
    global bunsen_gripper_status
    global bunsen_command

    # print(msg.topic + " " + str(json_msg))
    #print(type(msg.payload.decode("utf-8")))

    if "gripper_status" in msg.topic:
        #print("gripper_status: {}".format(msg.payload.decode("utf-8")))
        bunsen_gripper_status = msg.payload.decode("utf-8")
        flags[STATUS_UPDATE] = True
    elif "position" in msg.topic:
        json_msg = json.loads(msg.payload.decode("utf-8"))
        # print(
        #     "position: x: {}, y: {}, z: {}, w: {}, b: {}, r: {}".format(
        #         json_msg[0],
        #         json_msg[1],
        #         json_msg[2],
        #         json_msg[3],
        #         json_msg[4],
        #         json_msg[5],
        #     )
        # )
        bunsen_position = json_msg
        flags[POSITION_UPDATE] = True
    elif "command" in msg.topic:
        # print("command: {}".format(msg.payload.decode("utf-8")))
        bunsen_command = msg.payload.decode("utf-8")
        flags[COMMAND_UPDATE] = True


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

print("Starting loop")
client.loop_start()

for i in range(3):
    # First, wait for Bunsen to tell us its position
    while flags[POSITION_UPDATE] == False:
        pass

    # Move to die position
    input("Press enter to send 'command: open'")
    flags[POSITION_UPDATE] = False
    client.publish("Beaker/command", "open")

    # Move to new position
    input("Press enter to send 'position: []'")
    client.publish("Beaker/position", json.dumps([580, -580, 200, -90, 60, -179]))

    # Second, wait for Bunsen to ask us to release the die
    while flags[COMMAND_UPDATE] == False:
        pass

    input("Press enter to send 'gripper_status: open'")
    flags[COMMAND_UPDATE] = False
    client.publish("Beaker/gripper_status", "open")

client.loop_stop()

# Robot A: Start server process

# Robot A: Subscribe to "$B/#" topic

# Robot B: Subscribe to "$A/#" topic

# Robot B: Wait on event from "$A/#" topic

# Robot A: Pick up block

# Robot A: Move block to random position

# Robot A: publish data as json to "$A/#" topic

# Robot A: Wait on event from "$B/#"

# Robot B: Receives position data from "$A/#" topic

# Robot B: Moves to block's position

# Robot B: Close gripper around block

# Robot B: Send event to "$A/#" with "open gripper" command

# Robot A: Receive "open gripper" from "$B/#" topic

# Robot A: Open gripper

# Robot A: Send event to "$B/#" with "gripper opened" command

# Example position data:
# {
#   "position": [522.718262, 5.908576, 96.417938, 179.9, 0, 30],
#   "command": "open_gripper",
#   "gripper_status": "open"
# }
