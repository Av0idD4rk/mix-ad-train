import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from services.auth_service import router as auth_router
from services.admin_service import router as admin_router
from services.photo_service import router as photo_router
from services.premium_service import router as premium_router
from shared.database import initialize_db

app = FastAPI()

initialize_db()

app.include_router(auth_router, prefix="/auth")
app.include_router(admin_router, prefix="/admin")
app.include_router(photo_router, prefix="/photo")
app.include_router(premium_router, prefix="/premium")
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/{page}.html")
async def serve_html(page: str):
    file_path = os.path.join("static", f"{page}.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    return {"error": "Page not found"}, 404

@app.get("/")
async def root():
    return FileResponse('static/index.html', media_type="text/html")

@app.get("/{page}")
async def serve_file(page: str):
    if os.path.exists(page):
        return FileResponse(page, media_type="text/html")
    return {"error": "Page not found"}, 404