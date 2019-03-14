"""
This file generates scenario files for AT 

Pre-requistes: 
  -- config.json - top level config 
  -- serialnum.txt - txt file containing equivalent number of serial numbers 
  -- userid.txt - txt file containing equivalent number of userids 
  -- scenarios/master_ext_info.json 
  -- scenarios/master_ext_report.json 
  -- scenarios/master_aps_mac_addr.txt
  -- scenarios/master_sta_mac_addr.txt
Output: 
  -- report files
  -- info files 
  -- mac_address block files

"""
import os 
import json
from collections import OrderedDict

g_config = {}

####### COMMON UTILITY FUNCTIONS ########

def get_json_config(json_file):
    """
    returns json object of a json file
    """
    fp = open(json_file)
    
    json_config = fp.read()
    fp.close()
    
    #return json.loads(json_config, object_pairs_hook=OrderedDict)
    return json.loads(json_config)

def write_json(file_name, data):
    
    fp = open(file_name, "w")
    #print "Name of the file: ", fp.name
    #print "Closed or not : ", fp.closed
    #print "Opening mode : ", fp.mode
        
    #json.dump(data, fp)
    fp.write(str(json.dumps(data)))
    fp.close()
        
    """
    Remove extra spaces    
    """
    """
    r_data = ''
    try:
        fp = open(file_name, "r+")
        r_data = fp.read()
        #remove all whitespace characters 
        r_data = ''.join(r_data.split())
        fp.seek(0)
        fp.write(r_data)
    
    finally:
        fp.close()
    """

####### COMMON UTILITY FUNCTIONS ########

def load_config(config_file):
    """
    Loads the complete config at init time
    """
    global g_config
    g_config = get_json_config(config_file)
    get_master_ext_json()
    
    g_config['mac_file_index'] = 0
    g_config['mac_file_fp'] = 0
    
    #Add sta_fp to g_config for persistence    
    file_path = g_config['scenarios']['path']
    sta_file = g_config['scenarios']['sta_mac_file']
    sta_file_name = file_path + sta_file 
    fp_sta = open(sta_file_name, 'r')
    g_config['fp_sta'] = fp_sta
    
    #print g_config
    
    
def generate_userids(num_users = 100000, user_prefix = 'SIMUL_V1_'):
    """
    vne::tbd to generate different userIds with provided user_prefix
    """
    
    global g_config
    file_path = g_config['scenarios']['path']
    
    block_start = 10000001
    prefix = user_prefix
    id_file = prefix + str(num_users) + '.txt'
    
    
    #Windows: f_name = file_path + '\\' + id_file
    f_name = file_path + '/' + id_file
    print 'Writing user file: ' + f_name
    fp = open(f_name, 'w')
    
    for count in range(block_start, block_start + num_users):
        #print prefix + str(count)
        fp.write(prefix + str(count) + '\n')
    fp.close()
    
    g_config['singlejson']['userid_file'] = f_name
    g_config['userid_file'] = f_name
    
    pass

def generate_serialnos(num_users, sno_prefix):
    """
    vne::tbd to generate different serial_nos with provided sno_prefix
    """
    pass

def get_master_ext_json():
    """
    loads master json
    """
    global g_config
    file_path = g_config['scenarios']['path']
    
    master_ext_report = g_config['scenarios']['ext']['report']
    #windows: master_ext_report_json = get_json_config('\\'.join([file_path, master_ext_report]))
    master_ext_report_json = get_json_config('/'.join([file_path, master_ext_report]))
    g_config['master_ext_report_json'] = master_ext_report_json
    
    master_ext_info = g_config['scenarios']['ext']['info']
    #windows: master_ext_info_json = get_json_config('\\'.join([file_path, master_ext_info]))
    master_ext_info_json = get_json_config('/'.join([file_path, master_ext_info]))
    g_config['master_ext_info_json'] = master_ext_info_json
    
    master_rg_info = g_config['scenarios']['rg']['info']
    #windows: master_rg_info_json = get_json_config('\\'.join([file_path, master_rg_info]))
    master_rg_info_json = get_json_config('/'.join([file_path, master_rg_info]))
    g_config['master_rg_info_json'] = master_rg_info_json
    
    master_rg_report = g_config['scenarios']['rg']['report']
    #windows: master_rg_report_json = get_json_config('\\'.join([file_path, master_rg_report]))
    master_rg_report_json = get_json_config('/'.join([file_path, master_rg_report]))
    g_config['master_rg_report_json'] = master_rg_report_json
    
    g_config['singlejson'] = {}
    master_rg_single_json_path = g_config['scenarios']['single_json_file']
    #windows: g_config['singlejson']['master_rg_json'] = get_json_config('\\'.join([file_path, master_rg_single_json_path]))
    g_config['singlejson']['master_rg_json'] = get_json_config('/'.join([file_path, master_rg_single_json_path]))
    
    #windows: g_config['scenarios']['ext']['path'] = g_config['scenarios']['path'] + '\\' + 'ext' + '\\'
    #windows: g_config['scenarios']['rg']['path'] = g_config['scenarios']['path'] + '\\' + 'rg' + '\\'
    g_config['scenarios']['ext']['path'] = g_config['scenarios']['path'] + '/' + 'ext' + '/'
    g_config['scenarios']['rg']['path'] = g_config['scenarios']['path'] + '/' + 'rg' + '/'

    print 'master jsons loaded '
    
  
    
    
def generate_user_ext_report_json(user_id,serial_no):
    """
    generates json file for a AP (ext)
    
    -- open a copy of master scenario json file with name: ext/<user_id_sno>.json
    -- update userId and sno prefix 
    -- write that file into disk
    """
    global g_config
    
    file_path = g_config['scenarios']['path']
    m_sc_json = g_config['master_ext_report_json']
    #windows: f_name = file_path + '\\ext\\' + '_'.join(['report', user_id, serial_no]) + '.json'
    f_name = file_path + '/ext/' + '_'.join(['report', user_id, serial_no]) + '.json'
    
    m_sc_json['result'][0]['UserId'] = user_id
    m_sc_json['result'][0]['DevList'][0]['SerialNumber'] = serial_no
    
    ## STALIST MACs DISTRIBUTION - 5 MACs per radio 
    #Hardcoded logic:: It assumes master report json contains 5 devices STA list per Radio 
    for count in range(0,2):
        for count1 in range(0,5):
            m_sc_json['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][count]['SSID'][0]['STAList'][count1]['MACAddress'] = g_config['fp_sta'].readline().strip()
            #BSSIDs mapping between INFO and REPORT message
            bssids = get_ext_bssid_mappings(user_id,serial_no, 'ext')
            m_sc_json['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][count]['SSID'][0]['STAList'][count1]['BSSID'] = bssids[count]
            #print 'bssids ', bssids
    
    # + 1 MAC Address for STAList of MoCA Interface
    m_sc_json['result'][0]['DevList'][0]['Set'][0]['MoCA'][0]['STAList'][0]['MACAddress'] = g_config['fp_sta'].readline().strip()
    
    write_json(f_name, m_sc_json)
    print 'created report scenario file: ', f_name
    
    
def generate_user_ext_info_json(user_id,serial_no):
    """
    generates info json file for a AP (ext)
    
    -- open a copy of master scenario json file with name: ext/<user_id_sno>.json
    -- update userId and sno prefix 
    -- write that file into disk
    """
    global g_config
    
    file_path = g_config['scenarios']['path']
    m_sc_json = g_config['master_ext_info_json']
    #windows: f_name = file_path + '\\ext\\' + '_'.join(['info', user_id, serial_no]) + '.json'
    f_name = file_path + '/ext/' + '_'.join(['info', user_id, serial_no]) + '.json'
    
    m_sc_json['result'][0]['UserId'] = user_id
    m_sc_json['result'][0]['DevInfo'][0]['SerialNumber'] = serial_no
    
    #Open its mac block file name as use pick its first two mac addresses
    #windows: f_mac_name = file_path + '\\ext\\' + '_'.join(['mac_block', user_id, serial_no]) + '.txt'
    f_mac_name = file_path + '/ext/' + '_'.join(['mac_block', user_id, serial_no]) + '.txt'
    fp_mac_name = open(f_mac_name, 'r')
    
    ### Assign addresses to each of Radio of Wifi Interface from its mac block
    m_sc_json['result'][0]['DevInfo'][0]['WiFi']['Radio'][0]['SSID'][0]['BSSID'] = fp_mac_name.readline().strip()
    m_sc_json['result'][0]['DevInfo'][0]['WiFi']['Radio'][1]['SSID'][0]['BSSID'] = fp_mac_name.readline().strip()
    ### Asssign Mac Address to WAN Interface from its mac block 
    m_sc_json['result'][0]['DevInfo'][0]['WAN']['MACAddress'] = fp_mac_name.readline().strip()
    ### MoCA Interface MAC Address from its mac block 
    m_sc_json['result'][0]['DevInfo'][0]['MoCA'][0]['MACAddress'] = fp_mac_name.readline().strip()
    
    ### 4 Mac Addresses used 
    
    
    fp_mac_name.close()
    
    write_json(f_name, m_sc_json)
    print 'created scenario file: ', f_name
    
def generate_ext_report_scenarios(num_exts):
    """
    Generates ext_scenario files
    
    
    Report Message Generation 
      -- open userids and serial number files 
      -- pick them and generate individual scenarios
      -- update files 
    """
    
    """
    REPORT MESSAGE GENERATION
    """
    
    global g_config
    uid_file = g_config['user_ids']
    sno_file = g_config['serial_nums']
    
    fp_uid = open(uid_file, 'r')
    fp_sno = open(sno_file, 'r')
    
    for count in range(0, num_exts):
        uid = fp_uid.readline().strip()
        sno = fp_sno.readline().strip()
        print 'Extenders:: generating report scenario for: ', uid, sno 
        generate_user_ext_report_json(uid, sno)
    
    fp_uid.close()
    fp_sno.close()
    
def generate_ext_info_scenarios(num_exts):
    """
    Generates ext_scenario files
    
    Report Message Generation 
      -- open userids and serial number files 
      -- pick them and generate individual scenarios
      -- update files 
      
    Info Message Generation 
      -- Generates MAC addresses blocks
    """
        
    """
    INFO MESSAGE GENERATION  :: TBD
    """
    #Generate MAC address blocks
    #generate_ap_mac_blocks(16)
       
    global g_config
    uid_file = g_config['user_ids']
    sno_file = g_config['serial_nums']
    
    fp_uid = open(uid_file, 'r')
    fp_sno = open(sno_file, 'r')
    
    for count in range(0, num_exts):
        uid = fp_uid.readline().strip()
        sno = fp_sno.readline().strip()
        print 'Extenders:: generating info scenario for: ', uid, sno 
        generate_ap_mac_blocks_v1(16, uid, sno, 'ext')
        generate_user_ext_info_json(uid, sno)
    
    fp_uid.close()
    fp_sno.close()

# Updated function to support profiles and RG & Ext mapping
def generate_ext_report_scenarios_v1(uid, sno_list):
    """
    Generates ext_scenario files
    
    
    Report Message Generation 
      -- open userids and serial number files 
      -- pick them and generate individual scenarios
      -- update files 
    """
    
    """
    REPORT MESSAGE GENERATION
    """
    for sno in sno_list:
        print 'Extenders:: generating report scenario for: ', uid, sno 
        generate_user_ext_report_json(uid, sno)

def generate_ext_info_scenarios_v1(uid, sno_list):
    """
    Generates ext_scenario files
    
    Report Message Generation 
      -- open userids and serial number files 
      -- pick them and generate individual scenarios
      -- update files 
      
    Info Message Generation 
      -- Generates MAC addresses blocks
    """
        
    """
    INFO MESSAGE GENERATION  :: TBD
    """
    for sno in sno_list:
        print 'Extenders:: generating info scenario for: ', uid, sno 
        generate_ap_mac_blocks_v1(16, uid, sno, 'ext')
        generate_user_ext_info_json(uid, sno)
        

def get_ext_bssid_mappings(user_id, serial_no, gw_type):
    """
    Picks up bssids from INFO Message 
    gw_type: can be 'rg' or 'ext'
    """
    
    #Open INFO scenario file and get BSSID of each Wifi Radio
    global g_config
    
    file_path = g_config['scenarios']['path']
    #windows: f_info_name = file_path + '\\' + gw_type + '\\' + '_'.join(['info', user_id, serial_no]) + '.json'
    f_info_name = file_path + '/' + gw_type + '/' + '_'.join(['info', user_id, serial_no]) + '.json'
    
    info_json = get_json_config(f_info_name)
    bssid0 = info_json['result'][0]['DevInfo'][0]['WiFi']['Radio'][0]['SSID'][0]['BSSID']
    bssid1 = info_json['result'][0]['DevInfo'][0]['WiFi']['Radio'][1]['SSID'][0]['BSSID']
    
    return [bssid0, bssid1]
       

def generate_ext_scenarios(num_exts):    
    """
    Generates ext scenarios files 
    """
    #Maintain this order of generation of INFO message followed by REPORT Message. 
    #This is required to map BSSID from INFO to REPORT
    generate_ext_info_scenarios(num_exts)
    generate_ext_report_scenarios(num_exts)

########## RG Section ################
    
def generate_user_rg_report_json(user_id,serial_no):
    """
    generates json file for a AP (rg)
    
    -- open a copy of master scenario json file with name: rg/<user_id_sno>.json
    -- update userId and sno prefix 
    -- write that file into disk
    """
    global g_config
    
    file_path = g_config['scenarios']['path']
    m_sc_json = g_config['master_rg_report_json']
    #windows: f_name = file_path + '\\rg\\' + '_'.join(['report', user_id, serial_no]) + '.json'
    f_name = file_path + '/rg/' + '_'.join(['report', user_id, serial_no]) + '.json'
    
    m_sc_json['result'][0]['UserId'] = user_id
    m_sc_json['result'][0]['DevList'][0]['SerialNumber'] = serial_no
    
    ## STALIST MACs DISTRIBUTION - 3 MACs per radio 
    #Hardcoded logic:: It assumes master report json contains 5 devices STA list per Radio 
    hindex = 0
    for count in range(0,2):
        for count1 in range(0,5):
            m_sc_json['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][count]['SSID'][0]['STAList'][count1]['MACAddress'] = g_config['fp_sta'].readline().strip()
            m_sc_json['result'][0]['DevList'][0]['Set'][0]['HostsList'][hindex]['MACAddress'] = m_sc_json['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][count]['SSID'][0]['STAList'][count1]['MACAddress']
            hindex += 1
            #BSSIDs mapping between INFO and REPORT message
            bssids = get_ext_bssid_mappings(user_id,serial_no, 'rg')
            m_sc_json['result'][0]['DevList'][0]['Set'][0]['WiFi']['Radio'][count]['SSID'][0]['STAList'][count1]['BSSID'] = bssids[count]
            #print 'bssids ', bssids
    
    # + 1 MAC Address for STAList of MoCA Interface
    m_sc_json['result'][0]['DevList'][0]['Set'][0]['MoCA'][0]['STAList'][0]['MACAddress'] = g_config['fp_sta'].readline().strip()
    
    write_json(f_name, m_sc_json)
    print 'created report scenario file: ', f_name
    
    
def generate_rg_report_scenarios(num_rgs):
    """
    Generates rg_scenario files
    
    
    Report Message Generation 
      -- open userids and serial number files 
      -- pick them and generate individual scenarios
      -- update files 
    """
    
    """
    REPORT MESSAGE GENERATION
    """
    
    global g_config
    uid_file = g_config['user_ids']
    #sno_file = g_config['serial_nums']
    
    #STA Mac Address List generation 
    #Open Mac address files
    file_path = g_config['scenarios']['path']
    sta_file = g_config['scenarios']['sta_mac_file']
    sta_file_name = file_path + sta_file 
       
    fp_uid = open(uid_file, 'r')
    #fp_sno = open(sno_file, 'r')
    
    for count in range(0, num_rgs):
        uid = fp_uid.readline().strip()
        #sno = fp_sno.readline().strip()
        print 'Residential Gateways (RGs):: generating report scenario for: ', uid, uid 
        generate_user_rg_report_json(uid, uid)
    
    fp_uid.close()
    #fp_sno.close()
    
    


def generate_user_rg_info_json(user_id,serial_no):
    """
    generates info json file for a AP (rg)
    
    -- open a copy of master scenario json file with name: rg/<user_id_sno>.json
    -- update userId and sno prefix 
    -- write that file into disk
    """
    global g_config
    
    file_path = g_config['scenarios']['path']
    m_sc_json = g_config['master_rg_info_json']
    #windows: f_name = file_path + '\\rg\\' + '_'.join(['info', user_id, serial_no]) + '.json'
    f_name = file_path + '/rg/' + '_'.join(['info', user_id, serial_no]) + '.json'
    
    m_sc_json['result'][0]['UserId'] = user_id
    m_sc_json['result'][0]['DevInfo'][0]['SerialNumber'] = serial_no
    
    #Open its mac block file name as use pick its first two mac addresses
    #windows: f_mac_name = file_path + '\\rg\\' + '_'.join(['mac_block', user_id, serial_no]) + '.txt'
    f_mac_name = file_path + '/rg/' + '_'.join(['mac_block', user_id, serial_no]) + '.txt'
    fp_mac_name = open(f_mac_name, 'r')
    
    ### Assign addresses to each of Radio of Wifi Interface from its mac block
    m_sc_json['result'][0]['DevInfo'][0]['WiFi']['Radio'][0]['SSID'][0]['BSSID'] = fp_mac_name.readline().strip()
    m_sc_json['result'][0]['DevInfo'][0]['WiFi']['Radio'][1]['SSID'][0]['BSSID'] = fp_mac_name.readline().strip()
    ### Asssign Mac Address to WAN Interface from its mac block 
    m_sc_json['result'][0]['DevInfo'][0]['WAN']['MACAddress'] = fp_mac_name.readline().strip()
    ### MoCA Interface MAC Address from its mac block 
    m_sc_json['result'][0]['DevInfo'][0]['MoCA'][0]['MACAddress'] = fp_mac_name.readline().strip()
    
    ### 4 Mac Addresses used 
    
    
    fp_mac_name.close()
    
    write_json(f_name, m_sc_json)
    print 'created scenario file: ', f_name
    
def generate_rg_info_scenarios(num_rgs):
    """
    Generates rg_scenario files
    
    Report Message Generation 
      -- open userids and serial number files 
      -- pick them and generate individual scenarios
      -- update files 
      
    Info Message Generation 
      -- Generates MAC addresses blocks
    """
        
    """
    INFO MESSAGE GENERATION  :: TBD
    """
    #Generate MAC address blocks
    #generate_ap_mac_blocks(16)
       
    global g_config
    uid_file = g_config['user_ids']
    #sno_file = g_config['serial_nums']
    
    fp_uid = open(uid_file, 'r')
    #fp_sno = open(sno_file, 'r')
    uid_list = []
    
    for count in range(0, num_rgs):
        uid = fp_uid.readline().strip()
        #sno = fp_sno.readline().strip()
        print 'Residential Gateways (RGs):: generating info scenario for: ', uid, uid
        generate_ap_mac_blocks_v1(16, uid, uid, 'rg')
        generate_user_rg_info_json(uid, uid)
        uid_list.append(uid)
    
    fp_uid.close()
    #fp_sno.close()
    return uid_list
    
def generate_rg_scenarios(num_rgs):    
    """
    Generates rg scenarios files 
    """
    #Maintain this order of generation of INFO message followed by REPORT Message. 
    #This is required to map BSSID from INFO to REPORT
    generate_rg_info_scenarios(num_rgs)
    generate_rg_report_scenarios(num_rgs)    

def generate_ap_mac_blocks(block_size):
    """
    Generates mac address blocks from master file
    """
    global g_config
    num_aps = g_config['num_aps']
    file_path = g_config['scenarios']['path']
    
    #Open Mac address files
    mac_file = g_config['scenarios']['ap_mac_file']
    mac_file_name = file_path + mac_file 
    fp_mac = open(mac_file_name)
    
    #Open user id and serial number files
    uid_file = g_config['user_ids']
    sno_file = g_config['serial_nums']
    
    fp_uid = open(uid_file, 'r')
    fp_sno = open(sno_file, 'r')
    
    for count in range(0, num_aps):
        uid = fp_uid.readline().strip()
        sno = fp_sno.readline().strip()
        #windows: f_name = file_path + '\\ext\\' + '_'.join(['mac_block', uid, sno]) + '.txt'
        f_name = file_path + '/ext/' + '_'.join(['mac_block', uid, sno]) + '.txt'
        fp_1 = open(f_name, 'w')
        for count1 in range(0, block_size):
            fp_1.write(fp_mac.readline())
        fp_1.close()
        print 'MAC block written for: ', f_name
    
    fp_mac.close()
    fp_uid.close()
    fp_sno.close()
    

def generate_ap_mac_blocks_v1(block_size, usrid, srlno, gwtype):
    """
    Generates mac address blocks from master file
    block_size = number of MAC addresses in each block 
    usrid = user id 
    srlno = serial number 
    gwtype = gateway - a string - 'rg' or 'ext'
    """
    global g_config
    num_aps = g_config['num_aps']
    file_path = g_config['scenarios']['path']
    
    #Open Mac address files
    mac_file = g_config['scenarios']['ap_mac_file']
    mac_file_name = file_path + mac_file 
    
    if g_config['mac_file_index'] is 0:
        fp_mac = open(mac_file_name)
        g_config['mac_file_fp'] = fp_mac
    else: 
        fp_mac = g_config['mac_file_fp']
    
    g_config['mac_file_index'] += block_size
    
    #windows: f_name = file_path + '\\' + gwtype + '\\' + '_'.join(['mac_block', usrid, srlno]) + '.txt'
    f_name = file_path + '/' + gwtype + '/' + '_'.join(['mac_block', usrid, srlno]) + '.txt'
    fp_1 = open(f_name, 'w')
    for count1 in range(0, block_size):
        fp_1.write(fp_mac.readline())
    fp_1.close()
    print 'MAC block written for: ', f_name
    

def generate_scenarios():
    """
    It generates the scenarios based on loaded config
    
    """    
    global g_config
    
    profiles = g_config['scenarios']['profiles']
    #windows: profile_path= 'syn_file\\scenarios\\profiles\\'
    profile_path= 'syn_file/scenarios/profiles/'
    
    sno_file = g_config['serial_nums']
    fp_sno = open(sno_file, 'r')
    
    for prof in profiles:
        num_rg = prof['num_rg']
        num_ext = prof['num_ext']
        prof_name = prof['name']
        num_profiles = prof['num_profiles']
        f_profile_name = profile_path + '_'.join([prof_name, 'profile', str(num_profiles), str(num_rg), str(num_ext)]) + '.txt'
        fp_profile = open(f_profile_name, 'w')
        
        #Generate RGs scenario files 
        uid_list = generate_rg_info_scenarios(num_profiles)
        generate_rg_report_scenarios(num_profiles)
        
        #Now generate Extender Scenarios
        for uid in uid_list:
            sno_list = []
            fp_profile.write(uid + '\n')
            for count in range(0, num_ext):
                sno_list.append(fp_sno.readline().strip())
                fp_profile.write(sno_list[-1] + '\n')
            generate_ext_info_scenarios_v1(uid, sno_list)
            generate_ext_report_scenarios_v1(uid, sno_list)
    
    fp_sno.close()
    fp_profile.close()

def generate_scenarios_v3_latest():
    '''
    this function generates scenario files for v3 latest jsons - info and report for verizon specific 
    usecase, i.e. only RGWs, no extenders    
    '''
    global g_config
    
    sno_file = g_config['userid_file']
    f_usrid = open(sno_file, 'r')
    
    for usrid in f_usrid:
        uid = usrid.strip()
       
        generate_ap_mac_blocks_v1(5, uid, uid, 'rg')
        print 'Residential Gateways (RGs):: generating info scenario for: ', uid, uid
        generate_user_rg_info_json(uid, uid)
        print 'Residential Gateways (RGs):: generating report scenario for: ', uid, uid 
        generate_user_rg_report_json(uid, uid)
       
       
    

def generate_scenarios_single_json():
    """
    It generates the scenarios based on loaded config
    Based on Single JSON payload of RGW
        
    """    
    global g_config
    
    sno_file = g_config['singlejson']['userid_file']
      
    
    '''
    Open Single JSON master file: g_config['scenarios']['single_json_file']
    Create a directory 'singlejson'
    create rgw files in this directory for each g_config['singlejson']['userid_file']
    
    '''
    
    f_usrid = open(sno_file, 'r')
    
    for usrid in f_usrid:
        userid = usrid.strip()
        generate_ap_mac_blocks_single_json(10,userid)
        generate_singlejson_payload(userid)
    
   

def generate_ap_mac_blocks_single_json(block_size, usrid):
    """
    Generates mac address blocks from master file
    block_size = number of MAC addresses in each block 
    usrid = user id 
    """
    
    print 'generating mac block for ', usrid
    global g_config
    num_aps = g_config['num_aps']
    file_path = g_config['scenarios']['path']
    
    #Open Mac address files
    mac_file = g_config['scenarios']['ap_mac_file']
    mac_file_name = file_path + mac_file 
    
    if g_config['mac_file_index'] is 0:
        fp_mac = open(mac_file_name)
        g_config['mac_file_fp'] = fp_mac
    else: 
        fp_mac = g_config['mac_file_fp']
    
    g_config['mac_file_index'] += block_size
    
    #windows: f_name = file_path + '\\' + 'singlejson' + '\\' + '_'.join(['mac_block', usrid]) + '.txt'
    f_name = file_path + '/' + 'singlejson' + '/' + '_'.join(['mac_block', usrid]) + '.txt'
    fp_1 = open(f_name, 'w')
    for count1 in range(0, block_size):
        fp_1.write(fp_mac.readline())
    fp_1.close()
    print 'MAC block written for: ', f_name
    


def generate_singlejson_payload(user_id):
    """
  
    """
   
    global g_config
    
    file_path = g_config['scenarios']['path']
    m_sc_json = g_config['singlejson']['master_rg_json']
    #f_name = file_path + '\\singlejson\\' + '_'.join(['rgw', user_id]) + '.json'
    f_name = file_path + '/singlejson/' + '_'.join(['rgw', user_id]) + '.json'
    
    m_sc_json['UserId'] = user_id
    m_sc_json['Equipments'][0]['SerialNumber'] = user_id
        
    #Open its mac block file 
    #f_mac_name = file_path + '\\singlejson\\' + '_'.join(['mac_block', user_id]) + '.txt'
    f_mac_name = file_path + '/singlejson/' + '_'.join(['mac_block', user_id]) + '.txt'
    fp_mac_name = open(f_mac_name, 'r')
    
    ### Assign addresses to each of Radio of Wifi Interface from its mac block
    m_sc_json['Equipments'][0]['Messages'][0]['Info']['WAN']['MACAddress'] = fp_mac_name.readline().strip()
    m_sc_json['Equipments'][0]['Messages'][0]['Info']['SSID'][0]['BSSID'] = fp_mac_name.readline().strip()
    m_sc_json['Equipments'][0]['Messages'][0]['Info']['SSID'][1]['BSSID'] = fp_mac_name.readline().strip()
    m_sc_json['Equipments'][0]['Messages'][0]['Info']['SSID'][2]['BSSID'] = fp_mac_name.readline().strip()
    m_sc_json['Equipments'][0]['Messages'][0]['Info']['SSID'][3]['BSSID'] = fp_mac_name.readline().strip()
    m_sc_json['Equipments'][0]['Messages'][0]['Info']['MoCA'][0]['MACAddress'] = fp_mac_name.readline().strip()

    m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][0]['MACAddress'] = fp_mac_name.readline().strip()
    m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][1]['MACAddress'] = fp_mac_name.readline().strip()
    m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][2]['MACAddress'] = fp_mac_name.readline().strip()
    m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][3]['MACAddress'] = fp_mac_name.readline().strip()
    
    m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][0]['BSSID'] = m_sc_json['Equipments'][0]['Messages'][0]['Info']['SSID'][0]['BSSID']
    m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][1]['BSSID'] = m_sc_json['Equipments'][0]['Messages'][0]['Info']['SSID'][1]['BSSID']
    m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][2]['BSSID'] = m_sc_json['Equipments'][0]['Messages'][0]['Info']['SSID'][2]['BSSID']
    m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][3]['BSSID'] = m_sc_json['Equipments'][0]['Messages'][0]['Info']['SSID'][3]['BSSID']
        
    m_sc_json['Equipments'][0]['SmartSteeringLog'][0]['MACAddress'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][0]['MACAddress']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][0]['BSSID'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][1]['BSSID']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][1]['MACAddress'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][0]['MACAddress']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][1]['BSSID'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][1]['BSSID']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][2]['MACAddress'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][0]['MACAddress']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][2]['BSSID'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][1]['BSSID']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][3]['MACAddress'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][0]['MACAddress']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][3]['obssBSSID'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][1]['BSSID']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][3]['tbssBSSID'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][1]['BSSID']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][3]['ibssBSSID'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][1]['BSSID']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][4]['MACAddress'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][0]['MACAddress']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][6]['MACAddress'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][0]['MACAddress']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][6]['BSSID'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][1]['BSSID']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][7]['MACAddress'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][0]['MACAddress']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][7]['OBSSID'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][1]['BSSID']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][7]['NBSSID'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][1]['BSSID']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][8]['MACAddress'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][0]['MACAddress']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][8]['BSSID'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][1]['BSSID']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][9]['MACAddress'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][0]['MACAddress']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][9]['BSSID'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][1]['BSSID']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][10]['MACAddress'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][0]['MACAddress']
    m_sc_json['Equipments'][0]['SmartSteeringLog'][10]['BSSID'] = m_sc_json['Equipments'][0]['Messages'][0]['Report']['WiFiSTAList'][1]['BSSID']

    for index in range(0,11):
        m_sc_json['Equipments'][0]['SmartSteeringLog'][index]['SerialNumber'] = user_id

    fp_mac_name.close()
    
    write_json(f_name, m_sc_json)
    print 'created scenario file: ', f_name
      
               
def main():
    config_file = 'config1.json'

    global g_config
    load_config(config_file)
    
    '''
    For single JSON scenario files 
    '''
    generate_userids(g_config['num_aps'], g_config['profile_prefix'])
    generate_scenarios_single_json()
    
    
    
    # INFO + REPORT - v3 jsons - only RGW, no ext 
    #generate_userids(g_config['num_aps'], g_config['profile_prefix'])
    #generate_scenarios_v3_latest()
    
    ## New Version - report + info based 
    #generate_scenarios()
    
    ## Old version
    #generate_rg_scenarios(g_config['num_aps'])
    #generate_ext_scenarios(g_config['num_aps'])

 
if __name__ == '__main__':
    main()
