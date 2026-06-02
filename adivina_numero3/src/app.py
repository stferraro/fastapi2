import random

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Bienvenido al juego de adivinar el numero. Usa /api/adivina para iniciar el juego."}

@app.get("/api/adivina")
async def iniciar_juego():
    secret_number = random.randint(1, 100)
    return {"mensaje": "Adivina el numero entre 1 y 100.", "numero_secreto": secret_number}

@app.get("/api/adivina/{number}")
async def adivina_numero(number: int):
    secret_number = random.randint(1, 100)
    if number < secret_number:
        return {"mensaje": "Demasiado bajo. Intenta de nuevo.", "terminado": False}
    elif number > secret_number:
        return {"mensaje": "Demasiado alto. Intenta de nuevo.", "terminado": False}
    return {"mensaje": "Felicidades. Adivinaste el numero.", "terminado": True}
        
@app.get("/scalar", include_in_schema=False)
async def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Adivina Numero 3 - Scalar",
    )

