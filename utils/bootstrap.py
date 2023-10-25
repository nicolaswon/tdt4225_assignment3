from main.main import *

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