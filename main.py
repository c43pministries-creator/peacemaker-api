from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sqlite3
import time
import os
import requests

app = FastAPI(title="The Well of Peace & Peacemaker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WELL OF PEACE MODELS ---
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

# --- WELL OF PEACE ENDPOINTS ---
@app.get("/posts/{forum_id}", response_model=List[PostResponse])
def get_posts(forum_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT author, content, forum, timestamp FROM posts WHERE forum = ? ORDER BY timestamp ASC", (forum_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"author": row[0], "content": row[1], "forum": row[2], "timestamp": row[3]} for row in rows]

@app.post("/posts")
def create_post(post: Post):
    if "whatsapp" in post.content.lower() or "crypto" in post.content.lower():
        raise HTTPException(status_code=400, detail="Peace Shield Blocked.")

    conn = get_db()
    cursor = conn.cursor()
    current_time = time.time() * 1000 
    cursor.execute("INSERT INTO posts (author, content, forum, timestamp) VALUES (?, ?, ?, ?)", 
                   (post.author, post.content, post.forum, current_time))
    conn.commit()
    conn.close()
    return {"status": "success"}

# --- OWN U ENDPOINT ---
@app.post("/upload_id")
async def upload_id(file: UploadFile = File(...)):
    try:
        os.makedirs("id_uploads", exist_ok=True)
        file_path = f"id_uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        return {"status": "success", "message": "ID received successfully", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- NEW: THE PEACEMAKER WEB CHAT ENDPOINT ---
# REPLACE THIS URL WITH YOUR NGROK URL (e.g., https://xxxx-xx-xx-xx-xx.ngrok-free.app)
OLLAMA_URL = "https://belfast-nations-excited-mandatory.trycloudflare.com/api/generate" 
MODEL_NAME = "gemma:2b"

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    prompt = f"You are The Peacemaker. You are a companion, not a servant. You walk beside the user. Reply warmly and briefly to this message: '{request.message}'"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        ai_reply = response.json().get("response", "").strip()
        return {"reply": ai_reply}
    except Exception as e:
        print(f"Ollama Error: {e}")
        raise HTTPException(status_code=500, detail="The Peacemaker is having trouble connecting to the brain.")

@app.get("/")
def read_root():
    return {"message": "The Peacemaker Web Server is running."}