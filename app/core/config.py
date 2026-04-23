from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    ENV = os.getenv("ENV", "development")
    HOST = os.getenv("HOST","0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
    BASE_URL = os.getenv("BASE_URL")

settings = Settings()