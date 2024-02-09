import json
from time import sleep

import paho.mqtt.client as mqtt


def on_connect(client, user_data, flags, rc):
    print("Connected with result code " + str(rc))

    client.subscribe("robot_b/#")


def on_message(client, user_data, msg):
    json_msg = json.loads(msg.payload)
    # print(msg.topic + " " + str(json_msg))
    print(type(json_msg))

    if "gripper_open" in msg.topic:
        print("gripper_open: {}".format(json_msg))
    elif "position" in msg.topic:
        print(
            "position: x: {}, y: {}, z: {}, w: {}, b: {}, r: {}".format(
                json_msg[0],
                json_msg[1],
                json_msg[2],
                json_msg[3],
                json_msg[4],
                json_msg[5],
            )
        )
    elif "command" in msg.topic:
        print("command: {}".format(json_msg))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_start()

acc = 0
while True:
    client.publish("robot_a/position", acc)
    client.publish("robot_a/gripper_status", acc)
    acc += 1
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
