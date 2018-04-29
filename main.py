"""


"""

import paho.mqtt.client as mqtt
from bottle import route, run, Bottle


import os
import sys
import json
import socket
from random import randint
from time import sleep
from time import time
#from threading import Thread
import threading
import user




mqtt_rc_codes = {
                    0: 'Connection successful',
                    1: 'Connection refused - incorrect protocol version',
                    2: 'Connection refused - invalid client identifier',
                    3: 'Connection refused - server unavailable',
                    4: 'Connection refused - bad username or password',
                    5: 'Connection refused - not authorised'
                }

mqtt_profile = {}
g_config = {}
#Threads List 
g_ap_thr_list = []
#vne::tbd look at it laterr !
#g_config['ap_thr'] = ap_thr_list
#scenario specific configuration goes here
scenario_config = {}


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    #print("Connected with result code "+str(rc))
        
    global mqtt_rc_codes
    #if rc == 0:
    #    print 'Client connected successfully'
#       subscribe.subscribe_mqtt_topics(client)
    #else:
    #    print 'Client connection failed: ', str(rc), mqtt_rc_codes[rc]
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
    print("vne:: "+msg.topic+" "+str(msg.payload))
#    process_message(client, userdata, msg)
        
def on_publish(client, userdata, mid):
#    print("mid: "+str(mid))
    global scenario_config
    #print 'updating scenario config: ', userdata, scenario_config[userdata]['pub_cb_count']
    scenario_config[userdata]['pub_cb_count'] += 1
    pass


def start_mqtt(count, client_id, username = "", password = ""):
    global g_config
    global scenario_config
    
    srv_ip = g_config['broker_ip']
    srv_port = g_config['broker_port']
    srv_keepalive = g_config['keep_alive']
    clean_session = g_config['clean_session']

    # Get the lock
    g_config['thr_lock'].acquire()
    try:
        mqtt_client = mqtt.Client(client_id, clean_session, count)
    finally:
        g_config['thr_lock'].release()

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_publish = on_publish
    mqtt_client.on_disconnect = on_disconnect
    
    if username != "":
        mqtt_client.username_pw_set(username, password)

    if g_config['tls_enabled'] == 1:
        server_cert = g_config['server_crt']
        client_cert = g_config['client_crt']
        client_key = g_config['client_key']

#        print 'server cert:', server_cert
#        print 'client cert:', client_cert
#        print 'client key :', client_key
        mqtt_client.tls_set(server_cert, client_cert, client_key)
        mqtt_client.tls_insecure_set(True)
    
    mqtt_client.connect(srv_ip, srv_port, srv_keepalive, socket.gethostbyname(socket.gethostname()))
        
    scenario_config[count]['mqtt_client'] = mqtt_client
    
    #mqtt_client.loop_forever()
    mqtt_client.loop_start()
    #dpublish.read_device_data('temperature', '1', client)

####### COMMON UTILITY FUNCTIONS ########
def get_json_config(json_file):
    """
    returns json object of a json file
    """
    fp = open(json_file)
    
    json_config = fp.read()
    fp.close()
    return json.loads(json_config)

def open_n_readlines(file_name):
    
    lines = []
    
    try:
        fp = open(file_name, "r")
        #print "Name of the file: ", fp.name
        #print "Closed or not : ", fp.closed
        #print "Opening mode : ", fp.mode
        
        lines = fp.readlines()
    finally:
        fp.close()
    return lines
    
##########################################

def init_scenario_config(index):
    """
    Initializes scenario config values 
    """
    global scenario_config
    global g_config
    
    scenario_config[index]['index'] = index
    scenario_config[index]['Uptime'] = randint(1, 100000)
    scenario_config[index]['BytesSent'] = randint(1, 100000)
    scenario_config[index]['BytesReceived'] = randint(1, 100000)
    scenario_config[index]['mqtt_topic'] = '/'.join([g_config['mqtt_topic_prefix'], 
                           scenario_config[index]['user_id'].strip(), 
                           scenario_config[index]['serial_no'].strip()])
    #Publish count from paho callback 
    scenario_config[index]['pub_cb_count'] = 0
    scenario_config[index]['pub_info_count'] = 0
    scenario_config[index]['pub_report_count'] = 0

def get_info_payload(file_name):
    """
    vne::tbd:: hardcoded functions...to be replaced later with better functions
    """
    #file_name = 'syn_file/info.json'
    try:
        fp = open(file_name, "r")
        #print "Name of the file: ", fp.name
        #print "Closed or not : ", fp.closed
        #print "Opening mode : ", fp.mode
        
        line = fp.read()
    finally:
        fp.close()
    return line

def process_report_payload(index):
    """
    processes REPORT payload for its fields 
    input - index - AP index
    
     -- Change all the required fields and return
    """
    global scenario_config
    global g_config
    
    payload = scenario_config[index]['report_payload']
    #payload is in string format, it needs to be converted into json format first
    
    json_payload = json.loads(payload)
    
    ts_start = int(time())
    json_payload['id'] = int(ts_start)
    json_payload['result'][0]['TimestampStart'] = ts_start
    json_payload['result'][0]['TimestampEnd'] = ts_start
    
    json_payload['result'][0]['DevList'][0]['TimestampStart'] = ts_start
    json_payload['result'][0]['DevList'][0]['TimestampEnd'] = ts_start
    
    json_payload['result'][0]['DevList'][0]['Set'][0]['WAN']['BytesSent'] = scenario_config[index]['BytesSent']
    json_payload['result'][0]['DevList'][0]['Set'][0]['WAN']['BytesReceived'] = scenario_config[index]['BytesReceived']
    json_payload['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][0]['BytesSent'] = scenario_config[index]['BytesSent']
    json_payload['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][0]['BytesReceived'] = scenario_config[index]['BytesReceived']
    json_payload['result'][0]['DevList'][0]['Set'][0]['MoCA'][0]['BytesSent'] = scenario_config[index]['BytesSent']
    json_payload['result'][0]['DevList'][0]['Set'][0]['MoCA'][0]['BytesReceived'] = scenario_config[index]['BytesReceived']
    
    scenario_config[index]['report_payload'] = json.dumps(json_payload, indent=None, separators=(',',':'))
    
    #scenario_config[index]['BytesSent'] = scenario_config[index]['BytesSent'] + randint(1,100000)
    #scenario_config[index]['BytesReceived'] = scenario_config[index]['BytesReceived'] + randint(1,100000)
    
    #Copy timestamp to be used in INFO message
    scenario_config[index]['timestamp'] = ts_start
    #print 'sending report message: ', ts_start
    #vne::tbd, check if this can cause memory leak !
    
    
    
def process_info_payload(index):
    """
    processes INFO payload for its fields 
    input - index - AP index
    
     -- Change all the required fields and return
    """
    global scenario_config
    global g_config
    
    payload = scenario_config[index]['info_payload']
    #payload is in string format, it needs to be converted into json format first
    
    json_payload = json.loads(payload)
    
    #copy the timestamp of REPORT Message
    json_payload['id'] = scenario_config[index]['timestamp'] 
    json_payload['result'][0]['Timestamp'] = scenario_config[index]['timestamp'] 
    
    #change Uptime
    json_payload['result'][0]['DevInfo'][0]['Uptime'] = scenario_config[index]['Uptime'] 
    #scenario_config[index]['Uptime'] = scenario_config[index]['Uptime'] + scenario_config[index]['timestamp']
       
    scenario_config[index]['info_payload'] = json.dumps(json_payload, indent=None, separators=(',',':'))
    #print 'sending info message: ', ts_start
    #vne::tbd, check if this can cause memory leak ! 

def get_report_payload(file_name):
    """
    vne::tbd:: hardcoded functions...to be replaced later with better functions
    """
    #file_name = 'syn_file/report.json'
    #try:
    fp = open(file_name, "r")
        #print "Name of the file: ", fp.name
        #print "Closed or not : ", fp.closed
        #print "Opening mode : ", fp.mode
        
    line = fp.read()
    #finally:
    fp.close()
    return line


def load_scenario_config():
    """
    Loads scenario specific config files
    """
    global scenario_config
    global g_config
    
    user_id_file = g_config['user_ids']
    serial_num_file = g_config['serial_nums']
    
    uid_list = open_n_readlines(user_id_file)
    sid_list = open_n_readlines(serial_num_file)
    
    #print g_config
    #Filter uid_list and sid_list depending on ap_offset and num_aps
    start_offset = int(g_config['ap_offset']) * int(g_config['num_aps'])
    end_offset = start_offset + int(g_config['num_aps'])
    #print type(start_offset)
    #print type(end_offset)

    uid_list1 = uid_list[start_offset:end_offset]
    sid_list1 = sid_list[start_offset:end_offset]
    
    num_scenarios = g_config['num_aps']
    for count in range(0, num_scenarios):
        
        sc_cfg = {}
        #vne::tbd if local scope of this variable is not an issue 
        
        sc_cfg['user_id'] = uid_list1[count].strip()
        sc_cfg['serial_no'] = sid_list1[count].strip()

        #print  sc_cfg['user_id']
        #print  sc_cfg['serial_no']
        
        file_path = g_config['scenarios']['path'] + '/rg/'
        
        report_file = file_path + '_'.join(['report', sc_cfg['user_id'], sc_cfg['serial_no']]) + '.json'
        report_payload = get_report_payload(report_file)
        sc_cfg['report_payload'] = report_payload
        
        info_file = file_path + '_'.join(['info', sc_cfg['user_id'], sc_cfg['serial_no']]) + '.json'
        info_payload = get_info_payload(info_file)
        sc_cfg['info_payload'] = info_payload
        
        scenario_config[str(count)] = sc_cfg
        #print scenario_config
        #scenario_config[str(count)]['report_payload'] = sc_cfg['report_payload']
        #scenario_config[str(count)]['info_payload'] = sc_cfg['info_payload']


def load_scenario_config_v1():
    """
    Loads scenario specific config files
    v1 is for support of subscriber profiles 
    """
    global scenario_config
    global g_config
    
    profiles = g_config['scenarios']['profiles']
    profile_path= 'syn_file/scenarios/profiles/'
    
    ap_offset = int(g_config['ap_offset'])
    
    for prof in profiles:
        num_rg = prof['num_rg']
        num_ext = prof['num_ext']
        prof_name = prof['name']
        num_profiles = prof['num_profiles']
        
        #f_profile_name = profile_path + '_'.join([prof_name, 'profile', str(num_profiles), str(num_rg), str(num_ext)]) + '.txt'
        #vne:: hardcoded for now
        f_profile_name = profile_path + 'Home1_profile_100000_1_2.txt'
        fp_profile = open(f_profile_name, 'r')
        
        userid_list = []
        sno_list = []
        
        #Go to relative UserId and Serial number depending on specified ap_offset
        print 'Moving to offset: ', ap_offset * (num_profiles * (num_rg + num_ext))
        for count in range(0, ap_offset * (num_profiles * (num_rg + num_ext))):
            fp_profile.readline()       
        
        for count in range(0,num_profiles):
            userid_list.append(fp_profile.readline().strip())
            for count1 in range(0,num_ext):
                sno_list.append(fp_profile.readline().strip())
        
        scn_count = 0
        d_cnt = 1
        uid_idx = 0
        sid_idx = 0
        for count in range(0, len(userid_list) + len(sno_list)):
            if d_cnt == (num_rg + num_ext + 1): 
                 d_cnt = 1
                 uid_idx = uid_idx + 1

            sc_cfg = {}
            #vne::tbd if local scope of this variable is not an issue 
            sc_cfg['user_id'] = userid_list[uid_idx]
            userid = userid_list[uid_idx]
            serialno = sno_list[sid_idx]
            #print 'd_cnt : ', d_cnt
            if d_cnt == 1:
                sc_cfg['serial_no'] = userid
                sc_cfg['gw_type'] = 'rg'
                #print 'vne: creating rg', userid 
            else:
                sc_cfg['serial_no'] = serialno
                sc_cfg['gw_type'] = 'ext'
                sid_idx = sid_idx + 1
                #print 'vne: creating ext', serialno

            d_cnt = d_cnt + 1
            
            file_path = g_config['scenarios']['path'] + '/' + sc_cfg['gw_type'] + '/'      
            report_file = file_path + '_'.join(['report', sc_cfg['user_id'], sc_cfg['serial_no']]) + '.json'
            report_payload = get_report_payload(report_file)
            sc_cfg['report_payload'] = report_payload
    
            info_file = file_path + '_'.join(['info', sc_cfg['user_id'], sc_cfg['serial_no']]) + '.json'
            info_payload = get_info_payload(info_file)
            sc_cfg['info_payload'] = info_payload
    
            scenario_config[str(scn_count)] = sc_cfg
            #print 'Adding scenario config: ', scn_count
            #print scenario_config[str(scn_count)]
            #print 'Starting SNO: ', sc_cfg['serial_no']
            scn_count = scn_count + 1 
            #print scenario_config
    print 'Total profiles to run: ', len(scenario_config)
    print 'Start UserId: ', scenario_config['0']['user_id'] + '/' + scenario_config['0']['serial_no']
    print 'End UserId: ', scenario_config[str(scn_count - 1)]['user_id'] + '/' + scenario_config[str(scn_count - 1)]['serial_no']
    #print 'User list: ', userid_list
    #print 'Sno list: ', sno_list
    #print 'Scenario config: ', scenario_config
    g_config['num_aps'] = len(scenario_config)  



def load_config(config_file, ap_offset):
    """
    Loads the complete config at init time
    """
    global g_config
    g_config = get_json_config(config_file)
    #This offset will start AP with this number + num_aps to be executed in that process
    g_config['ap_offset'] = ap_offset

    # create a lock
    g_config['thr_lock'] = threading.Lock()
    
    # Scenario Specific Config
    #load_scenario_config()
    load_scenario_config_v1()

def publish_data(mqtt_client, topic, payload, mqtt_qos):
    """
    MQTT Publish with specified QoS 
    """
#    print 'publishing data:', topic

    #pub_data = json.dumps(payload)
    (rc, mid) = mqtt_client.publish(topic, payload, mqtt_qos)
    #(rc, mid) = mqtt_client.publish(topic, 'mqtt_test_tool', qos=1)
    
#    print 'published: ', rc, mid
    
def run_scenario(count):
    """
    Thread entry point that actually runs the scenario
    """
    global g_config
    global scenario_config
    sleep_time = 58
    
    scn_key = str(count)
    #print 'Scenario Started: ', count
        
    init_scenario_config(scn_key)
    mqtt_topic = scenario_config[scn_key]['mqtt_topic']
    
    ap_sno = scenario_config[scn_key]['serial_no'].strip()
    
    #start_mqtt(scn_key,  'vne_' + mqtt_topic, ap_sno, ap_sno)
    start_mqtt(scn_key,  'vne_' + mqtt_topic)
    
    while True:
        scenario_config[scn_key]['last_msg_ts'] = int(time())
        process_report_payload(count)
        #Requiremnt from Rohit: Keep Same timestamp in INFO & REPORT and send these two messages at same time
        scenario_config[scn_key]['pub_report_count'] += 1
        publish_data(scenario_config[scn_key]['mqtt_client'], mqtt_topic, scenario_config[scn_key]['report_payload'], g_config['qos'])
        #sleep(0.1)
        process_info_payload(count)
        scenario_config[scn_key]['pub_info_count'] += 1
        publish_data(scenario_config[scn_key]['mqtt_client'], mqtt_topic, scenario_config[scn_key]['info_payload'], g_config['qos'])
        sleep(sleep_time)
        ts_diff = int(time()) - scenario_config[scn_key]['last_msg_ts']
        if ts_diff > 60 : 
            print sleep_time, 'secs threshold exceeded for AP:', mqtt_topic, ts_diff
            
 
    
def start_scenario():
    """
    Start running the scenario
    """
    
    """
    vne::tbd make ap_thr_list a part of global config object
    """
    global g_config
    global g_ap_thr_list
    num_aps = g_config['num_aps']
    #print 'g_config: ', g_config
    #print 'number of APs: ',  num_aps
    
    #ap_thr_list = g_config['ap_thr']
    
    for count in range(0, num_aps):
        thr_count = str(count)
        #print 'thread count: ', thr_count
        # Start Gradually
        sleep(0.1)
        ap_thread = threading.Thread(target=run_scenario, args=(thr_count,))
        g_ap_thr_list.append(ap_thread)
        ap_thread.start()
    
    #start_rest_api()
    start_rest_api_nmt()

    print 'joining threads'
    for count in range(0, num_aps):
        g_ap_thr_list[count].join()
        

@route('/threads/active')
def get_active_thread():
     return str(threading.active_count())

@route('/threads')
def get_thread():
    global g_config 
    global scenario_config 

    resp_str = ''
    index = 0
    for index in range(0, g_config['num_aps']):
        resp_str += ', '.join([str(index),
                          scenario_config[str(index)]['mqtt_topic'],
                          str(scenario_config[str(index)]['pub_cb_count']), 
                          str(scenario_config[str(index)]['pub_info_count']), 
                          str(scenario_config[str(index)]['pub_report_count']),
                          '\n' 
                          ])
    return resp_str


##@g_config['api_bottle_fd'].route('/thread/<thr_id>')
@route('/thread/<thr_id>')
def get_thread_stats(thr_id):
    
    global scenario_config
    index = str(thr_id)

    #print 'get received: ', scenario_config[index]
    thr_stats = ', '.join([scenario_config[index]['mqtt_topic'],
                          str(scenario_config[index]['pub_cb_count']), 
                          str(scenario_config[index]['pub_info_count']), 
                          str(scenario_config[index]['pub_report_count']),
                          '\n' 
                          ])
    return thr_stats

def start_rest_api_nmt():
    """
    REST API interface function - non MT
    """
    global g_config
    base_port = 2000
    port_num = base_port + int(g_config['ap_offset'])
    g_config['api_bottle_ip'] = 'localhost'
    g_config['api_bottle_port'] = port_num
    print 'REST API started'

    run(host=g_config['api_bottle_ip'], port=g_config['api_bottle_port'])

    

def start_rest_api():
    """
    REST API interface function 
    """
    global g_config
    base_port = 2000
    port_num = base_port + int(g_config['ap_offset'])
    g_config['api_bottle_ip'] = 'localhost'
    g_config['api_bottle_port'] = port_num
    
    api_thread = threading.Thread(target=run_rest_api, args=(port_num,))
    g_config['api_thread_id'] = api_thread
    api_thread.start()
    api_thread.join()


def run_rest_api(port_num):
    
    global g_config
    
    #app = Bottle()
    #g_config['api_bottle_fd'] = app
    
    #run(app, host=g_config['api_bottle_ip'], port=g_config['api_bottle_port'])
    run(host=g_config['api_bottle_ip'], port=g_config['api_bottle_port'])


def main():
    
    global g_config
    if len (sys.argv) != 2 :
        print "Usage: python main.py <AP Offset>"
        sys.exit(1)   
    
    ap_offset = sys.argv[1]
    config_file = 'config1.json'

#    config_file = 'scenario.json'
    load_config(config_file, ap_offset)
    
    start_scenario()
    
if __name__ == '__main__':
    main()

