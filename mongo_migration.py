"""
File system to MongoDB Migration script

"""

import pymongo
# pprint library is used to make the output look more pretty
from pprint import pprint
import os 
import json

import mongo_connector

def load_profiles_from_db():
    """
    Loads rgw profiles from DB
    """
    g_config = {}
    g_config['profile_prefix'] = 'SIMUL_1V7_'
    config_id = 'config1'
    db_name = 'profiles'
    coll_name = g_config['profile_prefix'][:-1]

    mongo_client = pymongo.MongoClient(port = 27017)
   
    # Read rgw ids from rgw_profiles -> profile_prefix -> entries
    db_name = 'serialnos'
    coll_name = g_config['profile_prefix'][:-1]

    sample_size = 100
    mongo_db = mongo_client[db_name]
    rgw_records = mongo_db[coll_name].find().skip(100000).limit(sample_size)
    # Entries should be read in sorted order by their serial ids 
    print([document["user"] for document in rgw_records])

def migrate_serialnos(): 
    db_name = 'serialnos'
    coll_name = 'SIMUL_1V7'
    profile_path = 'syn_file/scenarios/'
    profile_file = 'SIMUL_1V7_1000000.txt'

    mongo_client = pymongo.MongoClient(port = 27017)
    mongo_db = mongo_client[db_name]
    mongo_db[coll_name].create_index([("user", pymongo.ASCENDING)], unique = True)
    
    fp_profile = open(profile_path + profile_file, 'r')
    count = 0

    for line in fp_profile:
       print 'inserting ', line, db_name, coll_name
       rgw_id = line.strip()
       record = { 'user' : rgw_id }
       result = mongo_db[coll_name].insert_one(record)
       pprint(result)
       count += 1 

    print 'RGWs processed', count

def migrate_profile():
    db_name = 'profiles'
    coll_name = 'SIMUL_1V7'
    profile_path = 'syn_file/scenarios/'
    profile_file = 'SIMUL_1V7_1000000.txt'
    #profile_file = 'SIMUL_V3_10.txt'
    rgw_path = profile_path + 'rg/'

    mongo_client = pymongo.MongoClient(port = 27017)
    mongo_db = mongo_client[db_name]
    mongo_db[coll_name].create_index([("user", pymongo.ASCENDING)], unique = True)
    
    fp_profile = open(profile_path + profile_file, 'r')
    count = 0

    for line in fp_profile:
       rgw_id = line.strip()
       #Open report, info and mac addr files for this rgw
       i_file = '_'.join(['info', rgw_id, rgw_id]) + '.json'
       r_file = '_'.join(['report', rgw_id, rgw_id]) + '.json'
       m_file = '_'.join(['mac_block', rgw_id, rgw_id]) + '.txt'

       with open(rgw_path + i_file) as fi: istr = fi.read().strip()
       with open(rgw_path + r_file) as fr: rstr = fr.read().strip()
       with open(rgw_path + m_file) as fm: mstr = fm.read().strip()
       #print istr, mstr, rstr
       record = { 'user' : rgw_id, 
                  'info' : istr,
                  'report' : rstr,
                  'mac_block' : mstr
                }
       result = mongo_db[coll_name].insert_one(record)
       pprint(result)
    
       count += 1 

    print 'RGWs processed', count

def tool_config():
    """
    Tool config to create provisioning records in mongo
    """
    config_file = 'config1.json'
    config_id = 'config1'

    db_name = 'tool_config'
    coll_name = 'provisioning'

    mongo_client = pymongo.MongoClient(port = 27017)
    mongo_db = mongo_client[db_name]
    mongo_db[coll_name].create_index([("config_id", pymongo.ASCENDING)], unique = True)

    with open(config_file) as fi: istr = fi.read().strip()
    #print istr, mstr, rstr
    record = { 'config_id' : config_id, 
               'config' : istr
             }

    result = mongo_db[coll_name].insert_one(record)
    pprint(result)
    print 'config added ', record

def get_config_from_db():
    
    config_id = 'config1'
    db_name = 'tool_config'
    coll_name = 'provisioning'

    mongo_client = pymongo.MongoClient(port = 27017)
    mongo_db = mongo_client[db_name]
   
    count = mongo_db[coll_name].find({'config_id' : config_id}).count()
    config = mongo_db[coll_name].find_one({'config_id' : config_id})
    print config['config']

def mongo_connect(): 
   # connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
   client = pymongo.MongoClient(port = 27017)
   db=client.admin
   # Issue the serverStatus command and print the results
   serverStatusResult=db.command("serverStatus")
   pprint(serverStatusResult)

def mongo_connector_test():
    mongo_conn = mongo_connector.mongo_connector()
    mongo_conn.dump_mongo_class()
    #record = mongo_conn.get_record('tool_config', 'provisioning', 'config_id', 'config1')
    record = mongo_conn.get_record('profiles', 'SIMUL_1V3', 'user', 'SIMUL_1V3_10000001')
    print record

def main(): 
   #migrate_profile()
   #tool_config()
   #get_config_from_db()
   #mongo_connector_test()
   #migrate_serialnos()
   load_profiles_from_db()

if __name__ == '__main__':
    main()
