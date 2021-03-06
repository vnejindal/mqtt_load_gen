"""


"""

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
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
import copy
import signal
from __builtin__ import False

import mongo_connector



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

g_steering_evt = {
                  'evid_assoc': 1,
                  'evid_staconnect': 1,
                  'evid_stainfo': 1,
                  'evid_staroam': 1,
                  'evid_ss': 1,
                  'evid_log_victim' : 1,
                  'evid_log_target': 1,
                  'evid_disassoc_ss' :1,
                  'evid_bsc': 0,
                  'evid_disassoc': 0,
                  'evid_stanum': 0
                 }

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    #print("Connected with result code "+str(rc) + client)
        
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
        print 'Client disconnected successfully '
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
    finally:
        g_config['thr_lock'].release()
        
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
                           scenario_config[index]['user_id'].strip()])
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

def get_steering_payload(file_name):
    return get_json_config(file_name)
    #return get_info_payload(file_name)

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
    
    ts_start = int(time()) #convert secs to minutes
    ts_start = ts_start - ts_start%60
    json_payload['id'] = int(ts_start)
    json_payload['isp'] = g_config['isp']
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
    
    json_payload['result'][0]['DevList'][0]['Set'][0]['CpuUsage'] = randint(0,100)
    json_payload['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][0]['SSID'][0]['STAList'][0]['RSSI'] = randint(-100,0)
    json_payload['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][0]['SSID'][0]['STAList'][1]['RSSI'] = randint(-100,0)
    json_payload['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][0]['SSID'][0]['STAList'][2]['RSSI'] = randint(-100,0)
    
    ## Fields filled to be used for Steering event message
    if g_config['steering_evt']['enabled'] is 1 and scenario_config[index]['steering']['ready'] is 0:
        scenario_config[index]['steering']['ready'] = 1
        scenario_config[index]['steering']['UserId'] = json_payload['result'][0]['UserId']
        #Transition of STA0 from 2.4G to 5G 
        scenario_config[index]['steering']['MACAddress'] = json_payload['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][0]['SSID'][0]['STAList'][0]['MACAddress']
        scenario_config[index]['steering']['BSSID'] = json_payload['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][1]['SSID'][0]['STAList'][0]['BSSID']
        for key in g_steering_evt.keys(): 
            #print key, g_steering_evt[key]
            if g_steering_evt[key] is 1: 
                j_payload = scenario_config[index]['steering'][key]['payload']
                j_payload['isp'] = g_config['isp']
                j_payload['result']['UserId'] = scenario_config[index]['steering']['UserId']
                j_payload['result']['SerialNumber'] = scenario_config[index]['steering']['UserId']
                j_payload['result']['MACAddress'] = scenario_config[index]['steering']['MACAddress']
                if key is 'evid_staroam': 
                    j_payload['result']['OBSSID'] = scenario_config[index]['steering']['BSSID']
                    j_payload['result']['NBSSID'] = scenario_config[index]['steering']['BSSID']
                elif key is 'evid_ss':
                    j_payload['result']['obssBSSID'] = scenario_config[index]['steering']['BSSID']
                    j_payload['result']['ibssBSSID'] = scenario_config[index]['steering']['BSSID']
                else:
                    j_payload['result']['BSSID'] = scenario_config[index]['steering']['BSSID']
    
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
    json_payload['isp'] = g_config['isp']
    json_payload['result'][0]['Timestamp'] = scenario_config[index]['timestamp'] 
    
    #change Uptime
    json_payload['result'][0]['DevInfo'][0]['Uptime'] = scenario_config[index]['Uptime'] 
    #scenario_config[index]['Uptime'] = scenario_config[index]['Uptime'] + scenario_config[index]['timestamp']
       
    scenario_config[index]['info_payload'] = json.dumps(json_payload, indent=None, separators=(',',':'))
    #print 'sending info message: ', ts_start
    #vne::tbd, check if this can cause memory leak ! 


def process_single_json_payload(index):
    """
    processes REPORT payload for its fields 
    input - index - AP index
    
     -- Change all the required fields and return
    """
    global scenario_config
    global g_config
    
    payload = scenario_config[index]['payload']
    #payload is in string format, it needs to be converted into json format first
    
    json_payload = json.loads(payload)
    
    ts_start = int(time()) # convert secs to minutes
    ts_start = ts_start - ts_start%60
    json_payload['SendingTime'] = int(ts_start)
    json_payload['Equipments'][0]['Messages'][0]['Timestamp'] = json_payload['SendingTime']
    json_payload['Equipments'][0]['ISP'] = g_config['isp']
    
    """    
    json_payload['result'][0]['DevList'][0]['Set'][0]['WAN']['BytesSent'] = scenario_config[index]['BytesSent']
    json_payload['result'][0]['DevList'][0]['Set'][0]['WAN']['BytesReceived'] = scenario_config[index]['BytesReceived']
    json_payload['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][0]['BytesSent'] = scenario_config[index]['BytesSent']
    json_payload['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][0]['BytesReceived'] = scenario_config[index]['BytesReceived']
    json_payload['result'][0]['DevList'][0]['Set'][0]['MoCA'][0]['BytesSent'] = scenario_config[index]['BytesSent']
    json_payload['result'][0]['DevList'][0]['Set'][0]['MoCA'][0]['BytesReceived'] = scenario_config[index]['BytesReceived']
    
    json_payload['result'][0]['DevList'][0]['Set'][0]['CpuUsage'] = randint(0,100)
    json_payload['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][0]['SSID'][0]['STAList'][0]['RSSI'] = randint(-100,0)
    json_payload['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][0]['SSID'][0]['STAList'][1]['RSSI'] = randint(-100,0)
    json_payload['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][0]['SSID'][0]['STAList'][2]['RSSI'] = randint(-100,0)
    """
    
    scenario_config[index]['payload'] = json.dumps(json_payload, indent=None, separators=(',',':'))    
    

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
            
            if len(g_config['user_auth_list']) != 0:
                sc_cfg['user_auth_list'] = g_config['user_auth_list'][g_config['user_auth_index']]
                sc_cfg['user_auth_index'] = g_config['user_auth_index']
                g_config['user_auth_index'] = (g_config['user_auth_index'] + 1) % len(g_config['user_auth_list'])
                #print 'sc config ', sc_cfg['user_auth_list']
                #print 'sc index', sc_cfg['user_auth_index']
    
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

def load_scenario_config_single_json():
    """
    Loads scenario specific config files
    v1 is for support of subscriber profiles 
    """
    global scenario_config
    global g_config
    
    #change delim
    delim = '/'
    profile_file = g_config['scenarios']['path'] + delim + g_config['profile_prefix_v4'] + str(g_config['num_aps']) + '.txt'
    ap_offset = int(g_config['ap_offset'])
    
    sample_size = g_config['sample_size']
    
    profile_offset = (ap_offset - 1) * sample_size + 1
    print 'Moving to offset: ', profile_offset
        
    fp_profile = open(profile_file, 'r')
  
    scn_count = 0
    
    for count in range(1, profile_offset):
        fp_profile.readline()  
    
    for count in range(0, sample_size):
        sc_cfg = {}
        sc_cfg['user_id'] = fp_profile.readline().strip();
        file_path = g_config['scenarios']['path'] + delim + 'singlejson' + delim      
        report_file = file_path + '_'.join(['rgw', sc_cfg['user_id']]) + '.json'
        report_payload = get_report_payload(report_file)
        sc_cfg['payload'] = report_payload
        
        if len(g_config['user_auth_list']) != 0:
            sc_cfg['user_auth_list'] = g_config['user_auth_list'][g_config['user_auth_index']]
            sc_cfg['user_auth_index'] = g_config['user_auth_index']
            #print 'user creds: ', sc_cfg['user_auth_list']
            g_config['user_auth_index'] = (g_config['user_auth_index'] + 1) % len(g_config['user_auth_list'])
    
        scenario_config[str(scn_count)] = sc_cfg
        #print 'Adding scenario config: ', scn_count
        #print scenario_config[str(scn_count)]
        #print 'Starting SNO: ', sc_cfg['serial_no']
        scn_count = scn_count + 1 
        #print scenario_config
    print 'Total profiles to run: ', len(scenario_config)
    print 'Start UserId: ', scenario_config['0']['user_id'] 
    print 'End UserId: ', scenario_config[str(scn_count - 1)]['user_id']
    #print 'User list: ', userid_list
    #print 'Sno list: ', sno_list
    #print 'Scenario config: ', scenario_config
    g_config['num_aps'] = len(scenario_config)  

def get_config_from_db():
    """
    gets config from mongodb connector class 
    """
    global g_config
    config_id = g_config['config_name']
    db_name = 'tool_config'
    coll_name = 'provisioning'
    record = g_config['mongo_connector'].get_record(db_name, coll_name, 'config_id', config_id)
    if record is None: 
        print 'Config does not exist in db.. ', config_id
        sys.exit(1)
    #print config['config']
    return json.loads(record['config'])


def get_profiles_from_db():
    """
    Loads rgw profiles from DB
    """
    global g_config
    global scenario_config

    db_name = 'serialnos'
    coll_name = g_config['profile_prefix'][:-1]

    # Read rgw ids from rgw_profiles -> profile_prefix -> entries
    ap_offset = int(g_config['ap_offset'])
    sample_size = g_config['sample_size']
   
    profile_offset = (ap_offset - 1) * sample_size 
    record_list = g_config['mongo_connector'].get_userids_list(db_name, coll_name, profile_offset, sample_size)

    scn_count = 0
    for rgw in record_list:
        sc_cfg = {}
        sc_cfg['user_id'] = rgw
        db_name = 'profiles'
        coll_name = g_config['profile_prefix'][:-1]
        record = g_config['mongo_connector'].get_record(db_name, coll_name, 'user', rgw)
        if record is None: 
             print 'Record does not exist in db.. ', rgw
             continue
        sc_cfg['report_payload'] = record['report']
        sc_cfg['info_payload'] = record['info']
        
        if len(g_config['user_auth_list']) != 0:
            sc_cfg['user_auth_list'] = g_config['user_auth_list'][g_config['user_auth_index']]
            sc_cfg['user_auth_index'] = g_config['user_auth_index']
            #print 'user creds: ', sc_cfg['user_auth_list']
            g_config['user_auth_index'] = (g_config['user_auth_index'] + 1) % len(g_config['user_auth_list'])
    
        scenario_config[str(scn_count)] = sc_cfg
        #print 'Adding scenario config: ', scn_count
        #print scenario_config[str(scn_count)]
        #print 'Starting SNO: ', sc_cfg['serial_no']
        scn_count = scn_count + 1 
        #print scenario_config
    print 'Total profiles to run: ', len(scenario_config)
    print 'Start UserId: ', scenario_config['0']['user_id'] 
    print 'End UserId: ', scenario_config[str(scn_count - 1)]['user_id']
    #print 'User list: ', userid_list
    #print 'Sno list: ', sno_list
    #print 'Scenario config: ', scenario_config
    g_config['num_aps'] = len(scenario_config)  


def load_scenario_config_json_v3():
    """
    For V3 jsons - info and report ; For verizon - no Ext. only RGWs    
    """
    global scenario_config
    global g_config
    
    if g_config['provmode'] is 'dbconfig': 
       get_profiles_from_db()
       return 

    #change delim
    delim = '/'
    profile_file = g_config['scenarios']['path'] + delim + g_config['profile_prefix_v3'] + str(g_config['num_aps']) + '.txt'
    ap_offset = int(g_config['ap_offset'])
    
    sample_size = g_config['sample_size']
    
    profile_offset = (ap_offset - 1) * sample_size + 1
    print 'Moving to offset: ', profile_offset
        
    fp_profile = open(profile_file, 'r')
  
    scn_count = 0
    
    for count in range(1, profile_offset):
        fp_profile.readline()  
    
    for count in range(0, sample_size):
        sc_cfg = {}
        sc_cfg['user_id'] = fp_profile.readline().strip();
        file_path = g_config['scenarios']['path'] + delim + 'rg' + delim      
        report_file = file_path + '_'.join(['report', sc_cfg['user_id'], sc_cfg['user_id']]) + '.json'
        report_payload = get_report_payload(report_file)
        sc_cfg['report_payload'] = report_payload
        
        info_file = file_path + '_'.join(['info', sc_cfg['user_id'], sc_cfg['user_id']]) + '.json'
        info_payload = get_report_payload(info_file)
        sc_cfg['info_payload'] = info_payload
        
        if len(g_config['user_auth_list']) != 0:
            sc_cfg['user_auth_list'] = g_config['user_auth_list'][g_config['user_auth_index']]
            sc_cfg['user_auth_index'] = g_config['user_auth_index']
            #print 'user creds: ', sc_cfg['user_auth_list']
            g_config['user_auth_index'] = (g_config['user_auth_index'] + 1) % len(g_config['user_auth_list'])
    
        scenario_config[str(scn_count)] = sc_cfg
        #print 'Adding scenario config: ', scn_count
        #print scenario_config[str(scn_count)]
        #print 'Starting SNO: ', sc_cfg['serial_no']
        scn_count = scn_count + 1 
        #print scenario_config
    print 'Total profiles to run: ', len(scenario_config)
    print 'Start UserId: ', scenario_config['0']['user_id'] 
    print 'End UserId: ', scenario_config[str(scn_count - 1)]['user_id']
    #print 'User list: ', userid_list
    #print 'Sno list: ', sno_list
    #print 'Scenario config: ', scenario_config
    g_config['num_aps'] = len(scenario_config)  


def load_steering_evt_files():
    """
    This function loads steering event files for sending    
    """
    global g_config
    global scenario_config
    
    #change delim
    delim = '/'
    for key in g_steering_evt.keys(): 
        #print key, g_steering_evt[key]
        if g_steering_evt[key] is 1: 
            sta_evid_file = delim.join([g_config['steering_evt']['sta_file_path'], g_config['steering_evt']['type'][key]['sta_'+key+'_file']])
            g_config['steering_evt'][key] = get_steering_payload(sta_evid_file)
    
    #Now distribute steering config to scenario files
    sample_size = g_config['sample_size']
    steering_percentage = g_config['steering_evt']['percent']
    
    for count in range(0, sample_size):
        scenario_config[str(count)]['steering'] = {}
        scenario_config[str(count)]['steering']['enabled'] = 0
        # This field will be used for filling info like userId, mac address etc from report msg. 
        #The message will ready to be sent only after this information is present
        scenario_config[str(count)]['steering']['ready'] = 0
        for key in g_steering_evt.keys(): 
            #print key, g_steering_evt[key]
            if g_steering_evt[key] is 1: 
                scenario_config[str(count)]['steering'][key] = {}  
            #print scenario_config[str(count)]['steering']
    
    steering_size = sample_size * steering_percentage/100
    for count in range(0, steering_size):
        #print 'enabled steering for ', count, steering_size
        index = str(count)
        scenario_config[index]['steering']['enabled'] = 1
        for key in g_steering_evt.keys(): 
            if g_steering_evt[key] is 1: 
                scenario_config[index]['steering'][key]['payload'] = copy.deepcopy(g_config['steering_evt'][key])
                scenario_config[index]['steering'][key]['enabled'] = g_config['steering_evt']['type'][key]['enabled']
                scenario_config[index]['steering'][key]['frequency'] = g_config['steering_evt']['type'][key]['frequency']
                #print 'steering evts loaded :', key


def load_config(config_file, ap_offset, json_ver, config_name = ''):
    """
    Loads the complete config at init time
    """
    global g_config

    #Change threading stack size
    print 'Current Thread stack size ', threading.stack_size()
    threading.stack_size(64*1024) #64KB
    print 'New Thread stack size ', threading.stack_size()
    
    #This offset will start AP with this number + num_aps to be executed in that process
    g_config['ap_offset'] = ap_offset
    g_config['json_ver'] = json_ver

    if config_name is not '': 
        g_config['provmode'] = 'dbconfig'
        g_config['config_name'] = config_name
        g_config['mongo_connector'] = mongo_connector.mongo_connector()
        g_config.update(get_config_from_db())
    else: 
        g_config['provmode'] = 'fileconfig'
        g_config.update(get_json_config(config_file))

    # create a lock
    g_config['thr_lock'] = threading.Lock()
    ## Load user auth list if it is present
    get_user_auth_list()

    # Scenario Specific Config
    # load_scenario_config()
    #load_scenario_config_v1()
    if g_config['json_ver'] == 'v4':
        print 'loading v4 version scenarios'
        load_scenario_config_single_json()
    elif g_config['json_ver'] == 'v3':
        print 'loading v3 version scenarios'
        load_scenario_config_json_v3()
    else:    
        print 'Invalid version format', g_config['json_ver']
        
    #Load steering event files 
    if g_config['steering_evt']['enabled'] is 1:
        #print 'load steering event files...'
        load_steering_evt_files()
        
        
def publish_data(mqtt_client, topic, payload, mqtt_qos):
    """
    MQTT Publish with specified QoS 
    """
#    print 'publishing data:', topic

    #pub_data = json.dumps(payload)
    (rc, mid) = mqtt_client.publish(topic, payload, mqtt_qos)
    #(rc, mid) = mqtt_client.publish(topic, 'mqtt_test_tool', qos=1)
    
#    print 'published: ', rc, mid


def publish_steering_events(scn_key, mqtt_topic, qos, evt_type):
    """
    Check and if required publish steering event
    """
    global g_config
    global scenario_config
    
    if scenario_config[scn_key]['steering']['enabled'] is not 1:
        #print 'steering not enabled ', scn_key
        return
    if scenario_config[scn_key]['steering']['ready'] is not 1: 
        #print 'steering not ready ', scn_key
        return
    
    ts_start = int(time()) #convert secs to minutes
    ts_start = ts_start - ts_start%60
    str_paylod = ""
    #Convert msg into JSON 
    #steering msg already is into json format
    
    json_payload = scenario_config[scn_key]['steering'][evt_type]['payload']
    json_payload['id'] = int(ts_start)
    json_payload['result']['Timestamp'] = int(ts_start)
    #Change msg back into string
    str_payload = json.dumps(json_payload, indent=None, separators=(',',':'))
    publish_data(scenario_config[scn_key]['mqtt_client'], mqtt_topic, str_payload, qos)
        
    
 
def run_scenario(count):
    """
    Thread entry point that actually runs the scenario
    """
    global g_config
    global scenario_config
    rfrequency = g_config['frequency'] - 2
    
    scenario_start = 0
    scn_key = str(count)
    #print 'Scenario Started: ', count
        
    init_scenario_config(scn_key)
    mqtt_topic = scenario_config[scn_key]['mqtt_topic']
    
    ## Get usernames and passwords if they are present 
    uname = ""
    passwd = ""
    
    if 'user_auth_list' in scenario_config[scn_key]:
        uname = scenario_config[scn_key]['user_auth_list'][0]
        passwd = scenario_config[scn_key]['user_auth_list'][1]
        
    start_mqtt(scn_key,  'vne_' + mqtt_topic, uname, passwd)
    #start_mqtt(scn_key,  'vne_' + mqtt_topic)

    ctime = scenario_config[scn_key]['last_msg_ts'] = time()
    if g_config['steering_evt']['enabled'] is 1:
        for key in g_steering_evt.keys(): 
            if g_steering_evt[key] is 1 and scenario_config[scn_key]['steering'][key]['enabled'] is 1:
                scenario_config[scn_key]['steering'][key]['last_msg_ts'] = ctime

    while True:
        ctime = time()
        #print "publishing data thread ", count, ctime, ltime 
        if (ctime - scenario_config[scn_key]['last_msg_ts']) > rfrequency or scenario_start is 0:
            #print "publishing info/report data ", scenario_config[scn_key]['user_id'], ctime, scenario_config[scn_key]['last_msg_ts'], rfrequency
            scenario_start = 1
            scenario_config[scn_key]['last_msg_ts'] = int(ctime)
            if g_config['json_ver'] == 'v4':
                process_single_json_payload(count)
                scenario_config[scn_key]['pub_report_count'] += 1
                publish_data(scenario_config[scn_key]['mqtt_client'], mqtt_topic, scenario_config[scn_key]['payload'], g_config['qos'])
            else: 
                process_report_payload(count)
                scenario_config[scn_key]['pub_report_count'] += 1
                publish_data(scenario_config[scn_key]['mqtt_client'], mqtt_topic, scenario_config[scn_key]['report_payload'], g_config['qos'])
                sleep(0.1)
                process_info_payload(count)
                scenario_config[scn_key]['pub_info_count'] += 1
                publish_data(scenario_config[scn_key]['mqtt_client'], mqtt_topic, scenario_config[scn_key]['info_payload'], g_config['qos'])
        
        if g_config['steering_evt']['enabled'] is 1:
            for key in g_steering_evt.keys(): 
                if g_steering_evt[key] is 1 and scenario_config[scn_key]['steering'][key]['enabled'] is 1:
                    if (ctime - scenario_config[scn_key]['steering'][key]['last_msg_ts']) > scenario_config[scn_key]['steering'][key]['frequency']:
                        #print 'publishing steering evt ',scenario_config[scn_key]['user_id'], ctime, key
                        scenario_config[scn_key]['steering'][key]['last_msg_ts'] = ctime
                        publish_steering_events(scn_key, mqtt_topic, g_config['qos'], key)
                        sleep(0.05)

        #scenario_config[scn_key]['mqtt_client'].loop()

        sleep(0.5)
        
        '''
        #NOT REQUIRED FOR NOW    
        sleep(rfrequency)
        ts_diff = int(time()) - scenario_config[scn_key]['last_msg_ts']
        if ts_diff > g_config['frequency'] : 
            print sleep_time, 'secs threshold exceeded for AP:', mqtt_topic, ts_diff
        '''    
 
    
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
    #start_rest_api_nmt()

    print 'joining threads'
    while True:
        for count in range(0, num_aps):
            if g_ap_thr_list[count].isAlive():
                g_ap_thr_list[count].join(1)
          
        
def get_user_auth_list():
    """
    This function loads MQTT user auth params if they are present
    """
    global g_config
    
    uauth_file = g_config['user_auth_file']
    
    if os.path.exists(uauth_file) is False:
        return False
    
    auth_list = []
    with open(uauth_file,"r") as fp:
        for line in fp:
            line = line.rstrip('\n')
            utmp = line.split(":")
            auth_list.append(utmp)
    
    g_config['user_auth_list'] = auth_list
    g_config['user_auth_index'] = 0
    
    return True
        
    
    
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
    base_port = 1500
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
    base_port = 1500
    port_num = base_port + int(g_config['ap_offset'])
    g_config['api_bottle_ip'] = 'localhost'
    g_config['api_bottle_port'] = port_num
    
#    api_thread = threading.Thread(target=run_rest_api, args=(port_num,))
#    g_config['api_thread_id'] = api_thread
#    api_thread.start()
#    api_thread.join()


def run_rest_api(port_num):
    
    global g_config
    
    #app = Bottle()
    #g_config['api_bottle_fd'] = app
    
    #run(app, host=g_config['api_bottle_ip'], port=g_config['api_bottle_port'])
    run(host=g_config['api_bottle_ip'], port=g_config['api_bottle_port'])

def handle_signal(signalNumber, frame):
    """
    signal handler for updating provisioning
    """
    print "Signal recieived ", signalNumber
    return 

def main():
    
    global g_config
    if len (sys.argv) != 4 :
        print "Usage: python main.py <v3|v4> <AP Offset> <tool_config>"
        sys.exit(1)   

    provmode = 'dbconfig'

    json_ver = sys.argv[1]
    ap_offset = sys.argv[2]
    config_name = sys.argv[3]
    config_file = 'config1.json'

    signal.signal(signal.SIGHUP, handle_signal)
#    config_file = 'scenario.json'
    load_config(config_file, ap_offset, json_ver, config_name)
    
    start_scenario()
    
if __name__ == '__main__':
    main()

