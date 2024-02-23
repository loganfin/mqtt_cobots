import json
import paho.mqtt.client as paho
import sys
sys.path.append(r"C:\Users\mauri\SchoolStuff\Spring Junior\CS453\Fanuc Python Driver\fanuc_ethernet_ip_drivers\src")
from robot_controller import robot

#robot_IP = '172.29.208.123' #bunsen

robot_IP = '172.29.208.124' #beaker

beaker = robot(robot_IP)

client = paho.Client()

coord = []

def on_message(client,userdata,msg):
    global coord
    sub = json.loads(msg.payload.decode())
    coord = sub

client.on_message = on_message

client.connect("localhost", 1883,60)
client.subscribe("beaker/status")

try:
    print("Press CTRL+C to exit")
    while True:
        client.loop()
        if(coord!=[]):
            beaker.write_cartesian(coord)
            beaker.start_robot()
            test = "move complete"
            post = json.dumps(test)
            client.publish("bunsen/status",post,0)
except:
    print("Disconnecting from the broker")

client.disconnect()