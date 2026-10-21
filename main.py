from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sqlite3

# Initialize the app
app = FastAPI(title="The Well of Peace API")

# Allow your website to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # During development, allow everything. We will lock this to your domain later.
    allow_methods=["*"],
    allow_headers=["*"],
)

# This is the shape of a Post
class Post(BaseModel):
    author: str
    content: str
    forum: str

# The Database setup
def get_db():
    conn = sqlite3.connect("well_of_peace.db")
    return conn

# Automatically create the table when the server starts
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT,
            content TEXT,
            forum TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Run the setup immediately
init_db()

# 1. The Endpoint the Website uses to GET posts
@app.get("/posts/{forum_id}", response_model=List[Post])
def get_posts(forum_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT author, content, forum FROM posts WHERE forum = ?", (forum_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"author": row[0], "content": row[1], "forum": row[2]} for row in rows]

# 2. The Endpoint the Android App uses to CREATE a post
@app.post("/posts")
def create_post(post: Post):
    # THE PEACE SHIELD GOES HERE
    if "whatsapp" in post.content.lower() or "crypto" in post.content.lower():
        raise HTTPException(status_code=400, detail="Peace Shield Blocked: Off-platform migration not allowed.")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts (author, content, forum) VALUES (?, ?, ?)", 
                   (post.author, post.content, post.forum))
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Post created successfully."}