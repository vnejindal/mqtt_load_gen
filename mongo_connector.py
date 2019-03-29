
import pymongo
# pprint library is used to make the output look more pretty
from pprint import pprint

class mongo_connector:
    db_ip = '127.0.0.1'
    db_port = 27017
    mongo_client = ''

    def __init__(self):
        print 'creating mongo connector class'
        self.mongo_client = pymongo.MongoClient(port = self.db_port)
    

    def dump_mongo_class(self):
        print 'mongo_client :', self.mongo_client
        print 'db_ip :', self.db_ip
        print 'db_port :', self.db_port



    def get_record(self, db_name, coll_name, key_name, key_value):
       mongo_db = self.mongo_client[db_name]
       record = mongo_db[coll_name].find_one({key_name : key_value})
       #print record
       return record

    def get_userids_list(self, db_name, coll_name, skip_size = 0, num_records = 1):
       """
       skip_size: num of records to be skipped
       num_records: num of records to be selected in DB
       """
       mongo_db = self.mongo_client[db_name]
       records = mongo_db[coll_name].find().skip(skip_size).limit(num_records)
       # Entries should be read in sorted order by their serial ids 
       record_list = []
       for document in records:
           record_list.append(document["user"])
       #print record_list
       return record_list
     
