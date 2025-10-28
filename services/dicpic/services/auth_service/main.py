from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import jwt
from config import JWT_SECRET
from shared.database import get_db

router = APIRouter()

class RegisterSchema(BaseModel):
    email: str
    password: str

class LoginSchema(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(data: RegisterSchema, db = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (data.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (data.email, data.password))
    db.commit()
    return {"msg": "registered"}

@router.post("/login")
def login(data: LoginSchema, db = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id, is_premium FROM users WHERE email = %s AND password = %s", (data.email, data.password))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode({"sub": str(user[0]), "email": data.email, "is_premium": bool(user[1])}, JWT_SECRET, algorithm="HS256")
    print(JWT_SECRET)
    return {"access_token": token}
