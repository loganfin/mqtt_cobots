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

coord = [-700,35,-335,100,.779,-179]

message = coord

print(type(coord))

#beaker.write_cartesian(coord)
#jscon.dumps will create the message into json language which will be sent to the 
#server and will then be read by the publisher then told to move.
post = json.dumps(message)
#beaker.start_robot()

client.publish("test/status",post,0)

#beaker.write_cartesian_position(-650,-345,-75,100,.779,-179)
#beaker.start_robot()

coord = [-650,-345,-75,100,.779,-179]
message = coord
post = json.dumps(message)
client.publish("test/status",post,0)



#beaker.schunk_gripper('open')
#beaker.schunk_gripper('close')

#beaker.schunk_gripper('open')
#beaker.write_cartesian_position(-700,35,-335,100,.779,-179)


#beaker.write_cartesian_position(-750,150,-925,8,22,139)
#beaker.start_robot()

