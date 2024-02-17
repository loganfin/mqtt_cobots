import json
import paho.mqtt.client as paho
import sys
import random
sys.path.append(r"C:\Users\mauri\SchoolStuff\Spring Junior\CS453\Fanuc Python Driver\fanuc_ethernet_ip_drivers\src")
from robot_controller import robot

client = paho.Client()
if(client.connect("localhost",1883,60)!=0):
    print("Could not connect to server")

robot_IP = '172.29.208.124' #beaker

beaker = robot(robot_IP)

coord = [-114,-218,-26,6,19,-11]

message = coord

#print(type(coord))

post = json.dumps(message)
client.publish("beaker/status",post,0)

coord = [-387,333,537,-26,-35,63]
message = coord
post = json.dumps(message)
client.publish("beaker/status",post,0)

