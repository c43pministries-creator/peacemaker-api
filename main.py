from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sqlite3
import time

app = FastAPI(title="The Well of Peace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

class Post(BaseModel):
    author: str
    content: str
    forum: str

class PostResponse(Post):
    timestamp: float

def get_db():
    conn = sqlite3.connect("well_of_peace.db")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT,
            content TEXT,
            forum TEXT,
            timestamp REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.get("/posts/{forum_id}", response_model=List[PostResponse])
def get_posts(forum_id: str):
    conn = get_db()
    cursor = conn.cursor()
    # We only want the latest 50 posts to keep it fast
    cursor.execute("SELECT author, content, forum, timestamp FROM posts WHERE forum = ? ORDER BY timestamp ASC", (forum_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"author": row[0], "content": row[1], "forum": row[2], "timestamp": row[3]} for row in rows]

@app.post("/posts")
def create_post(post: Post):
    if "whatsapp" in post.content.lower() or "crypto" in post.content.lower():
        raise HTTPException(status_code=400, detail="Peace Shield Blocked: Off-platform migration not allowed.")

    conn = get_db()
    cursor = conn.cursor()
    
    current_time = time.time() * 1000 
    cursor.execute("INSERT INTO posts (author, content, forum, timestamp) VALUES (?, ?, ?, ?)", 
                   (post.author, post.content, post.forum, current_time))
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Post created successfully."}