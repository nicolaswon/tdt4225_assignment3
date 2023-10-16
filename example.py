from pprint import pprint 
from DbConnector import DbConnector


class ExampleProgram:

    def __init__(self):
        self.connection = DbConnector()
        self.client = self.connection.client
        self.db = self.connection.db

    def create_coll(self, collection_name):
        collection = self.db.create_collection(collection_name)    
        print('Created collection: ', collection)

    def insert_documents(self, collection_name):
         # Dummy user data
        users = [
            {
                "user_id": 1,
                "has_label": True,
                "activities": [12345, 23456, 34567]
            },
            {
                "user_id": 2,
                "has_label": False,
                "activities": [67890, 78901]
            }
            # Add more user data as needed
        ]

        # Dummy activity data
        activities = [
            {
                "transport_mode": "walk",
                "start_date_time": "2021-10-15 10:00:00",
                "end_date_time": "2021-10-15 12:00:00",
                "user_id": 1
            },
            {
                "transport_mode": "car",
                "start_date_time": "2021-10-16 15:00:00",
                "end_date_time": "2021-10-16 16:30:00",
                "user_id": 2
            }
            # Add more activity data as needed
        ]

        # Dummy trackpoint data
        trackpoints = [
            {
                "lat": 10,
                "lon": 11,
                "altitude": 123,
                "date_time": "2021-10-15 10:30:00",
                "user_id": 1,
                "activity": 12345
            },
            {
                "lat": 15,
                "lon": 18,
                "altitude": 100,
                "date_time": "2021-10-16 15:15:00",
                "user_id": 2,
                "activity": 67890
            }
            # Add more trackpoint data as needed
        ]

        collection = self.db[collection_name]
        #collection.insert_many(users)
        collection.insert_many(activities)
        #collection.insert_many(trackpoints)
        
    def fetch_documents(self, collection_name):
        collection = self.db[collection_name]
        documents = collection.find({})
        for doc in documents: 
            pprint(doc)
        

    def drop_coll(self, collection_name):
        collection = self.db[collection_name]
        collection.drop()

        
    def show_coll(self):
        collections = self.client['test'].list_collection_names()
        print(collections)
         


def main():
    program = None
    try:
        program = ExampleProgram()
        program.create_coll(collection_name="activities")
        program.show_coll()
        program.insert_documents(collection_name="activities")
        program.fetch_documents(collection_name="activities")
        #program.drop_coll(collection_name="activities")
        # Check that the table is dropped
        program.show_coll()
    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()


if __name__ == '__main__':
    main()
