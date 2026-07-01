from fastapi import FastAPI
from usuario import Usuario

app = FastAPI(
    title="Lista de Usuarios", 
    description="API para gestionar lista de usuarios", 
    version="0.1.0"
)

usuarios = [
    Usuario(cedula="1234567890", nombre="Juan Perez"),
    Usuario(cedula="0987654321", nombre="Maria Gomez")
]

@app.get("/usuarios")
async def get_usuarios():
    return usuarios

@app.post("/usuarios")
async def add_usuario(usuario: Usuario):
    cedula_exists = any(u.cedula == usuario.cedula for u in usuarios)
    if cedula_exists:
        return {"error": "La cédula ya existe"}
    usuarios.append(usuario)
    return usuario

@app.delete("/usuarios/{cedula}")
async def delete_usuario(cedula: str):
    global usuarios
    usuarios = [u for u in usuarios if u.cedula != cedula]
    return {"message": "Usuario eliminado"}

@app.put("/usuarios/{cedula}")
async def update_usuario(cedula: str, usuario: Usuario):
    for i, u in enumerate(usuarios):
        if u.cedula == cedula:
            usuarios[i] = usuario
            return usuario
    return {"error": "Usuario no encontrado"}

@app.patch("/usuarios/{cedula}")
async def patch_usuario(cedula: str, usuario: Usuario):
    for i, u in enumerate(usuarios):
        if u.cedula == cedula:
            if usuario.nombre is not None:
                usuarios[i].nombre = usuario.nombre
            return usuarios[i]
    return {"error": "Usuario no encontrado"}
