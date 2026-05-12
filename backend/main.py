from fastapi import FastAPI
from dotenv import load_dotenv
import os

from routes.screening import router as screening_router

# Load .env file
load_dotenv()

# Access API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = FastAPI()

app.include_router(screening_router)