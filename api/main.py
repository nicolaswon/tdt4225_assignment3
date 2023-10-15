from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from api.routes import router as user_router
from connector.mongo_connector import MongoConnector


config = dotenv_values(".env")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the PyMongo tutorial!"}

@app.on_event("startup")
def startup_db_client():
    connector = MongoConnector()

    app.mongodb_client = connector.client
    app.database = connector.db

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

app.include_router(user_router, tags=["users"], prefix="/user")