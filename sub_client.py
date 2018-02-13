"""


"""

import paho.mqtt.client as mqtt

import os
import sys
import socket

mqtt_rc_codes = {
                    0: 'Connection successful',
                    1: 'Connection refused - incorrect protocol version',
                    2: 'Connection refused - invalid client identifier',
                    3: 'Connection refused - server unavailable',
                    4: 'Connection refused - bad username or password',
                    5: 'Connection refused - not authorised'
                }

g_config = {}

def fill_config():
    global g_config
    g_config['broker_ip'] = '18.217.120.198'
    g_config['broker_port'] = 1883
    g_config['keep_alive'] =  90
    g_config['clean_session'] = 0
    g_config['sub_topic'] = 'VNE_REPORT/#'
    g_config['msg_count'] = 0
    
    g_config['file_fp'] = open('sub.txt',"a+")


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    global g_config
    if rc == 0:
        print 'Client connected successfully'
        client.subscribe(g_config['sub_topic'])
    else:
        print 'Client connection failed: ', str(rc), mqtt_rc_codes[rc]
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #vne::tbd::later    client.subscribe("$SYS/#")

def on_disconnect(client, userdata, rc):
    if rc == 0:
        print 'Client disconnected successfully'
    else:
        print 'Client disconnection issue: ', str(rc)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #print("vne:: "+msg.topic+" "+str(msg.payload))
    global g_config
    g_config['file_fp'].write(msg.topic + " " + str(msg.payload) + '\n')
    g_config['msg_count'] = g_config['msg_count'] + 1
    #process_message(client, userdata, msg)
        
def on_publish(client, userdata, mid):
    print("mid: "+str(mid))
    pass

def start_mqtt(client_id="sub_client_vne"):
    global g_config
   
    srv_ip = g_config['broker_ip']
    srv_port = g_config['broker_port']
    srv_keepalive = g_config['keep_alive']
    clean_session = g_config['clean_session']

    mqtt_client = mqtt.Client(client_id, clean_session)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_publish = on_publish
    mqtt_client.on_disconnect = on_disconnect
    
    #mqtt_client.connect(srv_ip, srv_port, srv_keepalive, socket.gethostbyname(socket.gethostname()))
    mqtt_client.connect(srv_ip, srv_port, srv_keepalive)
    
    mqtt_client.loop_forever()
    
    

def main():
    print 'in main'
    global g_config
    fill_config()
    start_mqtt()
    
    g_config['file_fp'].close()
    
    
    
    
    
    
if __name__ == '__main__':
    main()
