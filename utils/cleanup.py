from main.main import *

program = None
try:
    program = BootstrapMongo()
    
    program.drop_coll(collection_name='User')
    program.drop_coll(collection_name='Activity')
    program.drop_coll(collection_name='TrackPoint')
    program.show_coll()

except Exception as e:
        print("ERROR: Failed to use database:", e)
finally:
    if program:
        program.connection.close_connection()