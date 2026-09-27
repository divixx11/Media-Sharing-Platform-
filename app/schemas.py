from typing import Optional
from fastapi_users import schemas
import uuid
from pydantic import BaseModel

class Postcreate(BaseModel):
    caption: str

class PostResponse(BaseModel):
    id: str
    caption: str
    url: str
    file_type: str
    file_name: str
    created_at: str

class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass