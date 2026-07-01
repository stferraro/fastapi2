from fastapi import FastAPI
from pydantic import BaseModel

class Usuario(BaseModel):
    cedula: str
    nombre: str
    
    