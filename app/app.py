from fastapi import FastAPI, HTTPException,File,UploadFile,Form,Depends
from app.schemas import Postcreate,PostResponse,UserRead,UserCreate,UserUpdate
from app.db import Post,create_db_and_tables,get_async_session,User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
import os
import shutil
import tempfile
import uuid
from app.users import auth_backend,current_active_user,fastapi_users

@asynccontextmanager
async def lifespan(app:FastAPI): # This will create the database for us as soon as the request is generated and make sure it handles the requests correctly and cleanely 
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend),prefix='/auth/jwt',tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate),prefix="/auth",tags=["auth"],)
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])

# text_posts = {
#     1: {"title": "New Post", "content": "Cool test post"},
#     2: {"title": "Python Tip", "content": "Use list comprehensions for cleaner loops."},
#     3: {"title": "Daily Motivation", "content": "Consistency beats intensity every time."},
#     4: {"title": "Fun Fact", "content": "The first computer bug was an actual moth found in a Harvard Mark II."},
#     5: {"title": "Update", "content": "Just launched my new project! Excited to share more soon."},
#     6: {"title": "Tech Insight", "content": "Async I/O in Python can massively speed up I/O-bound tasks."},
#     7: {"title": "Quote", "content": "Programs must be written for people to read, and only incidentally for machines to execute."},
#     8: {"title": "Weekend Plans", "content": "Might finally clean up my GitHub repos... or just play some Minecraft."},
#     9: {"title": "Question", "content": "What's the most underrated Python library you've ever used?"},
#     10: {"title": "Mini Announcement", "content": "New video drops tomorrow—covering the weirdest Python features."}
# }

# @app.get("/posts")
# def get_posts(limit: int = None):
#     if limit:
#         return list(text_posts.values())[:limit]
#     return text_posts

# @app.get("/posts/{id}")
# def get_post(id: int) -> PostResponse:
#     if id not in text_posts:
#         raise HTTPException(status_code=404, detail="Post not found")
#     return text_posts.get(id)

# @app.post("/posts")
# def create_post(post: Postcreate) -> PostResponse:
#     new_post = {"title": post.title,"content": post.content}
#     text_posts[max(text_posts.keys()) + 1] = new_post
#     return new_post

@app.post("/upload") # This will create a post when we will upload a file 
async def upload_file(
    file:UploadFile= File(...), # means The user must send a file with this request. (...) means required
    caption: str = Form(""), # Caption is optional because it has ("")
    user :User = Depends(current_active_user),
    session:AsyncSession= Depends(get_async_session) # means Give this endpoint a database session so I can interact with the database.
):
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        with open(temp_file_path, "rb") as temp_file:
            upload_result = await imagekit.files.upload(
                file=temp_file,
                file_name=file.filename,
                tags=["backend-upload"]
            )
        post = Post(
            user_id=str(user.id),
            caption=caption,
            url=upload_result.url,
            file_type="video" if file.content_type and file.content_type.startswith("video/") else "image",
            file_name=upload_result.name
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        file.file.close()

@app.get("/feed") # This completes the feed function which will give all of the posts 
async def get_feed(
    session:AsyncSession=Depends(get_async_session),
    current_user:User=Depends(current_active_user)
):
    result = await session.execute(
        select(Post).order_by(Post.created_at.desc())
    )
    posts = [row[0] for row in result.all()]
    result = await session.execute(
        select(User)
    )
    users = [row[0] for row in result.all()]
    user_dict = {
        u.id: u.email
        for u in users
    }
    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id":str(post.id),
                "user_id":str(post.user_id),
                "caption":post.caption,
                "url":post.url,
                "file_type":post.file_type,
                "file_name":post.file_name,
                "created_at":post.created_at.isoformat(),
                "is_owner":post.user_id == str(current_user.id),
                "email":user_dict.get(post.user_id,"Unknown")
            }
        )
    return {"posts":posts_data}

@app.delete("/posts/{post_id}")
async def delete_post(
    post_id:str,
    session: AsyncSession = Depends(get_async_session),
    current_user:User=Depends(current_active_user)
):
    try:
        result = await session.execute(
            select(Post).where(Post.id==post_id)
        )
        post = result.scalars().first()
        if not post:
            raise HTTPException(
                status_code=404,
                detail="Post not found"
            )
        if post.user_id != str(current_user.id):
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to delete this post"
            )
        await session.delete(post)
        await session.commit()
        return {
            "success":True,
            "message":"Post deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )