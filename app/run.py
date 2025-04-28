import uvicorn
from app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.run:app", port=8005, log_level="info", reload=True)
