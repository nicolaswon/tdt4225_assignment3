from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from api.models import User

router = APIRouter()

@router.post("/", response_description="Create a new user", status_code=status.HTTP_201_CREATED, response_model=User)
def create_user(request: Request, user: User = Body(...)):
    user = jsonable_encoder(user)
    new_user = request.app.database["users"].insert_one(user)
    created_user = request.app.database["users"].find_one(
        {"_id": new_user.inserted_id}
    )

    return created_user

@router.get("/", response_description="List all users", response_model=List[User])
def list_users(request: Request):
    users = request.app.database["users"].find()
    return users

@router.get("/{id}", response_description="Get a single user by id", response_model=User)
def find_user(id: str, request: Request):
    if (user := request.app.database["users"].find_one({"_id": id})) is not None:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} not found")
