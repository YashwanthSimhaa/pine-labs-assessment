import uvicorn
from app.main import app
from app.core.config import settings

if __name__ == "__main__":
    try:
        uvicorn.run(app, host=settings.HOST, port=settings.PORT)
    except KeyboardInterrupt:
        print("Application has stopped.")