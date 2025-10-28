import sqlite3
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from shared.database import get_db
import os
from fastapi.responses import PlainTextResponse

router = APIRouter()

class AdminRegisterSchema(BaseModel):
    username: str
    password: str

class AdminLoginSchema(BaseModel):
    username: str
    password: str

@router.post("/register")
def register_admin(data: AdminRegisterSchema, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM admin_accounts WHERE username = %s", (data.username,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Admin already exists")
    
    cursor.execute("INSERT INTO admin_accounts (username, password) VALUES (%s, %s)", (data.username, data.password))
    db.commit()
    return {"msg": "admin registered"}

@router.post("/login")
def login_admin(data: AdminLoginSchema, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM admin_accounts WHERE username = %s AND password = %s", (data.username, data.password))
    admin = cursor.fetchone()
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    token = f"admin-access-{admin[0]}"
    return {"admin_token": token}

@router.get("/photos")
def get_all_photos(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id, name, description, premium_only FROM photos")
    results = cursor.fetchall()
    return [{"id": row[0], "name": row[1], "description": row[2], "premium_only": bool(row[3])} for row in results]

@router.get("/users")
def list_users(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id, email, password, is_premium FROM users")
    results = cursor.fetchall()
    return [{"id": r[0], "email": r[1], "password": r[2], "is_premium": bool(r[3])} for r in results]
