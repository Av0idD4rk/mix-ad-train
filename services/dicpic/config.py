from dotenv import load_dotenv
import os

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "default_secret")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:qwerty123@db/dicpic")
