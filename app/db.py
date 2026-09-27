from collections.abc import AsyncGenerator
import uuid

from sqlalchemy import Column,String,Text,DateTime,ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession,create_async_engine,async_sessionmaker
from sqlalchemy.orm import DeclarativeBase,relationship
from datetime import datetime
from fastapi_users.db import SQLAlchemyUserDatabase,SQLAlchemyBaseUserTableUUID
from fastapi import Depends

DATABASE_URL = "sqlite+aiosqlite:///./test.db"  #sqlite+aiosqlite means= Use SQLite, but communicate with it using the aiosqlite Python driver.aiosqlite allows SQLite database operations to be performed asynchronously.

class Base(DeclarativeBase): #We cannot directly inherit from the DeclarativeBase so that's why we need this to pass the function 
    pass

class User(SQLAlchemyBaseUserTableUUID,Base):
    posts = relationship(argument="Post",back_populates="user")

# We need to specify what do we want to store for a post - maybe ID,Caption, Other things.

class Post(Base):
    __tablename__ = "posts" # Creates a table with the name "Posts"

    id = Column(String,primary_key=True,default=lambda: str(uuid.uuid4())) #Create a database table called posts, and give each post a unique UUID as its primary key.
# id = Column(...) means - Create a column called id in the posts table.
# UUID = Universally Unique Identifier. - A UUID is a large identifier designed to be extremely unlikely to collide with another UUID. Post 1 = Post 550e8400-e29b-41d4-a716-446655440000
# UUID(as_uuid=True) means Represent this UUID as a Python uuid.UUID object rather than just treating it as a string.
# primary_key = true means id is the primary key of this table
# default=uuid.uuid4 means When creating a new post, automatically generate a UUID for its id if one isn't provided.

    user_id = Column(String,ForeignKey("user.id"),nullable=False)
    caption = Column(Text)
    url = Column(String,nullable=False)
    file_type = Column(String,nullable = False)
    file_name = Column(String,nullable = False)
    created_at = Column(DateTime,default=datetime.utcnow)

    user = relationship(argument="User",back_populates="posts")

engine = create_async_engine(DATABASE_URL) # Here we are creating the Database engine

async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False
) # Creating a session maker(INSERT,UPDATE,SELECT,DELETE)

async def create_db_and_tables(): # Create the database tables if they don't already exist.
    async with engine.begin() as conn: #This opens a database connection and starts a transaction/context for the operations inside it.
        await conn.run_sync(Base.metadata.create_all) #metadata.create_all is the actual part that creates the table

async def get_async_session() -> AsyncGenerator[AsyncSession,None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)