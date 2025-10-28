from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
import jwt
from config import JWT_SECRET
from shared.database import get_db
from shared.key_validator import validate_key

router = APIRouter()

class PremiumSchema(BaseModel):
    key: str

@router.post("/buy")
def buy_premium(data: PremiumSchema, Authorization: str = Header(...), db = Depends(get_db)):
    try:
        scheme, token = Authorization.split()
        if scheme.lower() != "bearer":
            raise Exception("Invalid scheme")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload["sub"]
    except Exception as e:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    if not validate_key(data.key):
        raise HTTPException(status_code=401, detail="Invalid premium key")
    
    cursor = db.cursor()
    cursor.execute("UPDATE users SET is_premium = 1 WHERE id = %s", (user_id,))
    db.commit()
    cursor.execute("SELECT email, is_premium FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    token = jwt.encode({"sub": str(user_id), "email": user[0], "is_premium": bool(user[1])}, JWT_SECRET, algorithm="HS256")

    return {"access_token": token, "msg": "Поздравляем, вы получили премиум!"}
