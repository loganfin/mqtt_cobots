import json
import queue
import random
import sys
import threading
from time import sleep

# Location of robot_controller package
sys.path.append("./lib/fanuc_ethernet_ip_drivers/src")

import paho.mqtt.client as mqtt
from robot_controller import robot

events = {
    "position": threading.Event(),
    "command": threading.Event(),
    "status": threading.Event(),
}

queues = {
    "position": queue.Queue(),
    "command": queue.Queue(),
    "status": queue.Queue(),
}


# server_ip = "172.29.208.16"  # mauricio mosquitto
server_ip = "localhost" # local mosquitto
server_port = 1883
bunsen_ip = "172.29.208.123"

p = [
    [522, 6, 96.417938, 179.9, 0, 30],  # start position
    [580, -580, 200, -90, 60, -179],  # Basis for randomly generated position
    [522, 6, -194, -179.9, 0, 30],  # initial die position
]


def test_robot_range(client, robot, rng):
    print("Testing robot range")

    for i in range(2):
        if i == 0:
            x = rng
        else:
            x = -rng
        for j in range(2):
            if j == 0:
                y = rng
            else:
                y = -rng
            for k in range(2):
                if k == 0:
                    z = rng
                else:
                    z = -rng

                new_pos = p[1].copy()
                new_pos[0] += x
                new_pos[1] += y
                new_pos[2] += z

                if new_pos[2] < 40:
                    new_pos[2] = 40

                print(x, y, z)
                robot.write_cartesian_list(new_pos)


def move_robot(client, robot):
    # print("Moving robot")

    new_x = random.uniform(-200, 200)
    new_y = random.uniform(-200, 200)
    new_z = random.uniform(-200, 200)

    new_pos = p[1].copy()
    new_pos[0] += new_x
    new_pos[1] += new_y
    new_pos[2] += new_z

    if new_pos[2] <= 40:
        # print("AAAAH TOO LOW, old z: {}, new z: {}".format(new_pos[2], 40))
        new_pos[2] = 40

    robot.write_cartesian_list(new_pos)

    client.publish(
        "Bunsen/position", json.dumps(robot.read_current_cartesian_pose())
    )

    # sleep(1)


def pick_up_block(client, robot):
    # Go to initial die position
    robot.write_cartesian_list(p[2])

    robot.schunk_gripper("close")

    sleep(0.5)

    robot.write_cartesian_list(p[0])


def put_block_back(client, robot):
    # Go to initial die position
    robot.write_cartesian_list(p[2])

    robot.schunk_gripper("open")

    sleep(0.5)

    robot.write_cartesian_list(p[0])


def start_program(client, robot):
    # Reset
    robot.write_cartesian_list(p[0])
    sleep(0.5)
    robot.schunk_gripper("open")

    # test_robot_range(client, robot, 150)

    # Pick up block
    pick_up_block(client, robot)

    for _ in range(3):
        # First, move robot to a random position
        move_robot(client, robot)

        # Second, wait for Beaker to ask us to release the die
        events["command"].wait()
        beaker_command = queues["command"].get()

        if beaker_command == ["open"]:
            robot.schunk_gripper("open")
            client.publish("Bunsen/gripper_status", json.dumps(["open"]))
        else:
            print("Error, unknown command: {}".format(beaker_command))

        events["command"].clear()

        # Third, wait for Beaker to tell us their position
        events["position"].wait()
        beaker_position = queues["position"].get()

        # Back up a little bit to give the some space
        new_y = beaker_position[1]
        temp_pos = robot.read_current_cartesian_pose()
        temp_pos[1] = new_y + 200
        robot.write_cartesian_list(temp_pos)
        # sleep(0.5)

        # Approach straight on
        temp_pos_2 = beaker_position.copy()
        temp_pos_2[1] = new_y + 200
        robot.write_cartesian_list(temp_pos_2)
        # sleep(0.5)

        # how do we transform this to be correct?
        robot.write_cartesian_list(beaker_position)
        # Grab the block
        robot.schunk_gripper("close")

        events["position"].clear()

        # Tell Beaker to release the die
        client.publish("Bunsen/command", json.dumps(["open"]))

        # Fourth, wait for acknowledgement from Beaker
        events["status"].wait()
        beaker_gripper_status = queues["status"].get()

        if beaker_gripper_status != ["open"]:
            # Break out of the loop
            break

        # start next iteration
        events["status"].clear()

    # Replace block
    put_block_back(client, robot)

    client.loop_stop()


def on_connect(client, user_data, flags, rc):
    print("Connected with result code " + str(rc))

    client.subscribe("Beaker/#")


# This will run in the network thread
def on_message(client, user_data, msg):
    message = json.loads(msg.payload.decode("utf-8"))
    # print("Received: {}".format(message))
    if "gripper_status" in msg.topic:
        # print("gripper_status: {}".format(message))
        queues["status"].put(message)
        events["status"].set()
    elif "position" in msg.topic:
        # print("position: {}".format(json_msg))
        queues["position"].put(message)
        events["position"].set()
    elif "command" in msg.topic:
        # print("command: {}".format(message))
        queues["command"].put(message)
        events["command"].set()


if __name__ == "__main__":
    # Connect to Bunsen
    bunsen = robot(bunsen_ip)

    # Create MQTT client
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect

    # Connect to MQTT server
    client.connect(server_ip, server_port, 60)

    # Start program loop in the network thread
    client.loop_start()

    start_program(client, bunsen)
