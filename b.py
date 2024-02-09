import json
from time import sleep

import paho.mqtt.client as mqtt


def on_connect(client, user_data, flags, rc):
    print("Connected with result code " + str(rc))

    client.subscribe("robot_a/#")


def on_message(client, user_data, msg):
    print(msg.topic + " " + str(msg.payload))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_start()

gripper_open = True
position = [000, 100, 200, 300, 400, 500]
command = "open_gripper"

while True:
    client.publish("robot_b/gripper_open", json.dumps(gripper_open))
    client.publish("robot_b/position", json.dumps(position))
    client.publish("robot_b/command", json.dumps(command))

    gripper_open = not gripper_open

    if command == "open_gripper":
        command = "close_gripper"
    else:
        command = "open_gripper"

    sleep(1)

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
