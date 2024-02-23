import json
import paho.mqtt.client as paho
import sys
import random
import time
sys.path.append(r"C:\Users\mauri\SchoolStuff\Spring Junior\CS453\Fanuc Python Driver\fanuc_ethernet_ip_drivers\src")
from robot_controller import robot

robot_IP = '172.29.208.124' #beaker

beaker = robot(robot_IP)

client = paho.Client()

coord = None
Topic = ""

def on_message(client,userdata,msg):
    global coord, Topic
    sub = json.loads(msg.payload.decode())
    Topic = msg.topic 
    coord = sub

client.on_message = on_message

client.connect("localhost", 1883,60)
client.loop_start()
client.subscribe("Bunsen/#")

#try:

beaker.write_cartesian_position(485,-60,200,-179,2,30)
beaker.start_robot()

time.sleep(2)

beaker.write_cartesian_position(530, 580, 200, -90, 35, 0)
beaker.start_robot()

print("Press CTRL+C to exit")
while True:
    if(Topic == "Bunsen/position"):
        beaker.schunk_gripper('open')
        #The line will do the difference of the location
        #pose = beaker.read_current_cartesian_pose()
        coord[0] = coord[0]+55
        coord[1] = coord[1]+1100
        #coord[4] = coord[4]*-1
        coord[5] = 0
        beaker.write_cartesian(coord)
        beaker.start_robot()

        coord[1] = coord[1]+350
        beaker.write_cartesian(coord)
        beaker.start_robot()

        beaker.schunk_gripper('close')

        message = "open"
        post = json.dumps(message)
        client.publish("Beaker/command",post,0)
        Topic = ""

        time.sleep(1)

        temp = beaker.read_current_cartesian_pose()

        #move back after taking block
        temp[1] = temp[1]-200
        beaker.write_cartesian(temp)
        beaker.start_robot()

        #message = "open"
        #post = json.dumps(message)
        #client.publish("Beaker/command",post,0)
        #Topic = ""
    elif(Topic == "Bunsen/status"):
        #move to a random position
        coord = beaker.read_current_cartesian_pose()
        coord[0] = coord[0]+random.uniform(-150,150)
        coord[1] = coord[1]+random.uniform(-150,150)
        coord[2] = coord[2]+random.uniform(-150,150)
        if(coord[2]<-200):
            coord[2] = coord[2]+50
        print(coord)
        beaker.write_cartesian(coord)
        beaker.start_robot()
        #then send position to Bunsen
        #coord = beaker.read_current_cartesian_pose()
        #coord = [500,-218,-26,179,-1,-20]
        message = coord
        post = json.dumps(message)
        client.publish("Beaker/position",post,0)
        Topic = ""
    elif(Topic == "Bunsen/command"):
        if(coord != ""):
            beaker.schunk_gripper(coord)
            message = coord
            post=json.dumps(coord)
            client.publish("Beaker/status",post,0)
            Topic = ""
            #move back when you send the current position
            temp = beaker.read_current_cartesian_pose()
            temp[1] = temp[1]-200

            beaker.write_cartesian(temp)
            beaker.start_robot()
    elif(Topic == "Bunsen/finished"):
        if(coord != ""):
            beaker.write_cartesian_position(485,-60,200,-179,2,30)
            beaker.start_robot()
            coord = ""
#except:
#print("Disconnecting from the broker")
#client.loop_stop()
#client.disconnect()