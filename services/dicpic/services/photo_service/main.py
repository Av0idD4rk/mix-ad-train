import base64
import os
import re
import time
from urllib.parse import unquote
from fastapi import APIRouter, Depends, File, Form, HTTPException, Header, UploadFile, Request
from fastapi.responses import FileResponse, JSONResponse
import jwt
from config import JWT_SECRET
from shared.database import get_db

router = APIRouter()

@router.post("/upload")
def upload_photo(
    Authorization: str = Header(...),
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(...),
    premium_only: bool = Form(False),
    request: Request = None,
    db=Depends(get_db)
):
    try:
        scheme, token = Authorization.split()
        if scheme.lower() != "bearer":
            raise Exception("Invalid scheme")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload["sub"]
    except Exception as e:
        print(f"[ERROR] Token error in /upload: {e}")
        raise HTTPException(status_code=403, detail="Invalid token")

    contents = file.file.read()
    if len(contents) > 1024 * 512:
        raise HTTPException(status_code=400, detail="File too large")

    now = int(time.time())
    cursor = db.cursor()
    cursor.execute("SELECT last_upload_ts FROM photo_uploads WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    if row and now - row[0] < 10:
        raise HTTPException(status_code=429, detail="You must wait before uploading again")

    os.makedirs("uploads", exist_ok=True)
    filename = f"{int(time.time())}_{file.filename}"
    filepath = os.path.join("uploads", filename)
    with open(filepath, "wb") as f:
        f.write(contents)

    cursor.execute("INSERT INTO photos (author_id, name, description, premium_only, file_path) VALUES (%s, %s, %s, %s, %s)",
                   (user_id, name, description, int(premium_only), filepath))

    cursor.execute("INSERT INTO photo_uploads (user_id, last_upload_ts) VALUES (%s, %s)", (user_id, now))
    db.commit()

    return {"msg": "Photo uploaded successfully", "filename": filename}

def validate_query(q: str):
    decoded = unquote(q)
    if decoded != q:
        return
    forbidden = ["'", '"', ";", "--", "=", " OR ", " AND "]
    lowered = q.lower()
    for bad in forbidden:
        if bad.lower() in lowered:
            raise HTTPException(status_code=400, detail="Недопустимые символы в запросе")

@router.get("/search")
def search_photos(q: str = "", Authorization: str = Header(...), db=Depends(get_db)):
    try:
        scheme, token = Authorization.split()
        if scheme.lower() != "bearer":
            raise Exception("Invalid scheme")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload['sub']
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid token")

    validate_query(q)

    cursor = db.cursor()
    decoded_q = unquote(q)
    query = f"SELECT id, author_id, name, description, premium_only FROM photos WHERE name LIKE '%{decoded_q}%' OR description LIKE '%{decoded_q}%'"
    cursor.execute(query)
    rows = cursor.fetchall()

    results = []
    for id, author_id, name, description, premium_only in rows:
        if premium_only and not payload.get("is_premium", False) and str(author_id) != str(user_id):
            description = "Premium only"
        
        results.append({
            "id": id,
            "name": name,
            "description": description,
            "file_url": f"/photo/{id}/file"
        })

    return results

@router.get("/all_files")
def get_all_files(Authorization: str = Header(...), request: Request = None, db=Depends(get_db)):
    try:
        scheme, token = Authorization.split()
        if scheme.lower() != "bearer":
            raise Exception("Invalid scheme")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload["sub"]
    except Exception as e:
        raise HTTPException(status_code=403, detail="Invalid token")

    cursor = db.cursor()
    cursor.execute("SELECT id, author_id, file_path, premium_only, name, description FROM photos")
    rows = cursor.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="No photos found")

    result = []
    for photo_id, author_id, file_path, premium_only, name, description in rows:
        if premium_only and not payload.get("is_premium", False) and str(author_id) != str(user_id):
            file_base64 = None
            description = "Premium only"
        else:
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    file_bytes = f.read()
                file_base64 = "data:image/jpeg;base64," + base64.b64encode(file_bytes).decode('utf-8')
            else:
                file_base64 = None

        result.append({
            "id": photo_id,
            "author_id": author_id,
            "name": name,
            "description": description,
            "premium_only": premium_only,
            "file_base64": file_base64
        })

    return JSONResponse(content=result)

@router.get('/my')
def get_my_photos(Authorization: str = Header(...), db=Depends(get_db)):
    try:
        scheme, token = Authorization.split()
        if scheme.lower() != "bearer":
            raise Exception("Invalid scheme")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload["sub"]
    except Exception as e:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    cursor = db.cursor()
    cursor.execute("SELECT id, author_id, name, description, premium_only FROM photos WHERE author_id = %s", (user_id,))
    rows = cursor.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="No photos found")

    result = []
    for photo_id, author_id, name, description, premium_only in rows:

        result.append({
            "id": photo_id,
            "author_id": author_id,
            "name": name,
            "description": description,
            "premium_only": premium_only
        })

    return JSONResponse(content=result)

@router.get("/{photo_id}")
def get_photo(photo_id: int, Authorization: str = Header(...), db=Depends(get_db)):
    try:
        scheme, token = Authorization.split()
        if scheme.lower() != "bearer":
            raise Exception("Invalid scheme")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload["sub"]
    except Exception as e:
        print(f"[ERROR] Token error in /{photo_id}: {e}")
        raise HTTPException(status_code=403, detail="Invalid token")

    cursor = db.cursor()
    cursor.execute("SELECT author_id, name, description, premium_only, file_path FROM photos WHERE id = %s", (photo_id,))
    photo = cursor.fetchone()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if photo[3] and not payload.get("is_premium", False) and str(photo[0]) != str(user_id):
        raise HTTPException(status_code=403, detail="Premium required")

    return {
        "author_id": photo[0],
        "name": photo[1],
        "description": photo[2],
        "file_url": f"/photo/{photo_id}/file"
    }

@router.get("/{photo_id}/file")
def get_photo_file(photo_id: int, Authorization: str = Header(...), db=Depends(get_db)):
    try:
        scheme, token = Authorization.split()
        if scheme.lower() != "bearer":
            raise Exception("Invalid scheme")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload["sub"]
    except Exception as e:
        print(f"[ERROR] Token error in /{photo_id}: {e}")
        raise HTTPException(status_code=403, detail="Invalid token")

    cursor = db.cursor()
    cursor.execute("SELECT author_id, name, description, premium_only, file_path FROM photos WHERE id = %s", (photo_id,))
    photo = cursor.fetchone()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    author_id, name, description, premium_only, file_path = photo

    if premium_only and not payload.get("is_premium", False) and str(author_id) == str(user_id):
        raise HTTPException(status_code=403, detail="Premium required")
    
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        file_base64 =  "data:image/jpeg;base64," + base64.b64encode(file_bytes).decode('utf-8')
    else:
        file_base64 = None

    result = {
        "id": photo_id,
        "author_id": author_id,
        "name": name,
        "description": description,
        "premium_only": premium_only,
        "file_base64": file_base64
    }

    return JSONResponse(content=result)
