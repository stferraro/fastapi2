from fastapi import FastAPI
from config import title, description, version

app = FastAPI(title=title, description=description, version=version)

@app.get("/")
async def read_root():
    return {"message": "Hello World"}