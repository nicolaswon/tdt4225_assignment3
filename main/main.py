# from pymongo_get_database import get_database
from connector.mongo_connector import MongoConnector
from utils.schema_validator import user_validator, activity_validator, track_point_validator
from utils.collection_index import activity_index, track_point_index
from utils.load_pickle import users, activities, track_points
from pprint import pprint

# dbname = get_database()
# collection_name = dbname["users"]

class BootstrapMongo:
    def __init__(self):
        self.connection = MongoConnector()
        self.client = self.connection.client
        self.db = self.connection.db

    def create_coll(self, collection_name):
        collection = self.db.create_collection(collection_name)    
        print('Created collection: ', collection)

    def add_validator(self, collection_name, validator):
        self.db.command("collMod", collection_name, validator=validator)
        print("Added validator to collection: ", collection_name)

    def add_index(self, collection_name, index):
        collection = self.db[collection_name]
        collection.create_index(index)
        print("Added index to collection: ", collection_name)

    def insert_documents(self, collection_name, docs):
        collection = self.db[collection_name]
        collection.insert_many(docs)
        
    def fetch_documents(self, collection_name):
        collection = self.db[collection_name]
        documents = collection.find({})
        for doc in documents: 
            pprint(doc)
        

    def drop_coll(self, collection_name):
        collection = self.db[collection_name]
        collection.drop()

        
    def show_coll(self):
        collections = self.db.list_collection_names()
        print(collections)
         


def main():
    program = None
    try:
        program = BootstrapMongo()
        
        program.drop_coll(collection_name='User')
        program.drop_coll(collection_name='Activity')
        program.drop_coll(collection_name='TrackPoint')
        
        program.create_coll(collection_name="User")
        program.add_validator(collection_name="User", validator=user_validator)
        program.insert_documents(collection_name="User", docs=users)
        
        program.create_coll(collection_name="Activity")
        program.add_validator(collection_name="Activity", validator=activity_validator)
        program.add_index(collection_name="Activity", index=activity_index)
        program.insert_documents(collection_name="Activity", docs=activities)
        
        program.create_coll(collection_name="TrackPoint")
        program.add_validator(collection_name="TrackPoint", validator=track_point_validator)
        program.add_index(collection_name="TrackPoint", index=track_point_index)
        program.insert_documents(collection_name="TrackPoint", docs=track_points)
        
        program.show_coll()
    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()


if __name__ == '__main__':
    main()
