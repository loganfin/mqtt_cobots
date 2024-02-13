import sys

sys.path.append("./lib/fanuc_ethernet_ip_drivers/src")

import json
import random
from time import sleep

import paho.mqtt.client as mqtt
from robot_controller import robot

# Flags
flags = [False, False, False]

POSITION_UPDATE = 0
COMMAND_UPDATE = 1
STATUS_UPDATE = 2

beaker_position = []
beaker_gripper_status = ""
beaker_command = ""


server_ip = "localhost"
server_port = 1883
bunsen_ip = "172.29.208.123"

p = [
    [522, 6, 96.417938, 179.9, 0, 30],  # start position
    [580, -580, 200, -90, 60, -179],
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
    #print("Moving robot")

    new_x = random.uniform(-200, 200)
    new_y = random.uniform(-200, 200)
    new_z = random.uniform(-200, 200)

    new_pos = p[1].copy()
    new_pos[0] += new_x
    new_pos[1] += new_y
    new_pos[2] += new_z

    if new_pos[2] <= 40:
        #print("AAAAH TOO LOW, old z: {}, new z: {}".format(new_pos[2], 40))
        new_pos[2] = 40

    robot.write_cartesian_list(new_pos)

    client.publish(
        "Bunsen/position", json.dumps(robot.read_current_cartesian_pose())
    )

    #sleep(1)


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

    for i in range(3):
        # First, move robot to a random position
        move_robot(client, robot)
        # Second, wait for Beaker to ask us to release the die
        while flags[COMMAND_UPDATE] == False:
            pass

        #print(beaker_command)
        if beaker_command == "open":
            robot.schunk_gripper("open")
            client.publish("Bunsen/gripper_status", "open")
        flags[COMMAND_UPDATE] = False

        # Third, wait for Beaker to tell us their position
        while flags[POSITION_UPDATE] == False:
            pass

        # Back up a little bit to give the some space
        new_y = beaker_position[1]
        temp_pos = robot.read_current_cartesian_pose()
        temp_pos[1] = new_y + 200
        robot.write_cartesian_list(temp_pos)
        #sleep(0.5)

        # Approach straight on
        temp_pos_2 = beaker_position.copy()
        temp_pos_2[1] = new_y + 200
        robot.write_cartesian_list(temp_pos_2)
        #sleep(0.5)

        # how do we modify this to be correct?
        robot.write_cartesian_list(beaker_position)
        # Grab the block
        robot.schunk_gripper("close")

        flags[POSITION_UPDATE] = False
        # Tell Beaker to release the die
        client.publish("Bunsen/command", "open")

        # Fourth, wait for acknowledgement from Beaker
        while flags[STATUS_UPDATE] == False:
            pass

        if beaker_gripper_status == "open":
            pass
            flags[STATUS_UPDATE] = False
            # start next iteration
        else:
            break
            # cancel the program

    # Replace block
    put_block_back(client, robot)


def on_connect(client, user_data, flags, rc):
    print("Connected with result code " + str(rc))

    client.subscribe("Beaker/#")


def on_message(client, user_data, msg):
    global beaker_gripper_status
    global beaker_position
    global beaker_command

    message = msg.payload.decode("utf-8")
    #print("Received: {}".format(message))
    if "gripper_status" in msg.topic:
        #print("gripper_status: {}".format(message))
        beaker_gripper_status = message
        flags[STATUS_UPDATE] = True
    elif "position" in msg.topic:
        json_msg = json.loads(message)
        #print("position: {}".format(json_msg))
        beaker_position = json_msg
        flags[POSITION_UPDATE] = True
    elif "command" in msg.topic:
        #print("command: {}".format(message))
        beaker_command = message
        flags[COMMAND_UPDATE] = True


if __name__ == "__main__":
    # Connect to Bunsen
    bunsen = robot(bunsen_ip)

    # Create MQTT client
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect

    # Connect to MQTT server
    client.connect(server_ip, server_port, 60)

    # Start program loop
    client.loop_start()

    start_program(client, bunsen)
