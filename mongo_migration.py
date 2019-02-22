"""
File system to MongoDB Migration script

"""

import pymongo
# pprint library is used to make the output look more pretty
from pprint import pprint
import os 
import json


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

def mongo_connect(): 
   # connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
   client = pymongo.MongoClient(port = 27017)
   db=client.admin
   # Issue the serverStatus command and print the results
   serverStatusResult=db.command("serverStatus")
   pprint(serverStatusResult)

def main(): 
   migrate_profile()

if __name__ == '__main__':
    main()
