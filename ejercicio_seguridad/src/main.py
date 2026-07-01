from fastapi import FastAPI
from security import get_password_hash, verify_password

app = FastAPI()

@app.get("/")
async def read_root():
    contraseña = "mi_contraseña_segura"
    hash_contraseña = get_password_hash(contraseña)
    es_valida = verify_password(contraseña, hash_contraseña)
    return {"Hello": "World", "Contraseña válida": es_valida}