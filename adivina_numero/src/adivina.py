import random
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="adivina-numero-secreto")

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "src"), name="static")


def iniciar_juego(request: Request):
    request.session["numero_secreto"] = random.randint(1, 100)
    request.session["intentos"] = 0


@app.get("/")
async def mostrar_formulario():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/api/adivina")
async def preparar_juego(request: Request):
    iniciar_juego(request)
    return {"mensaje": "Adivina el numero entre 1 y 100.", "intentos": 0}

@app.get("/api/adivina/{numero}")
async def adivina_numero(numero: int, request: Request):
    if "numero_secreto" not in request.session:
        iniciar_juego(request)

    numero_secreto = request.session["numero_secreto"]
    intentos = request.session.get("intentos", 0) + 1
    request.session["intentos"] = intentos

    if numero < numero_secreto:
        return {"mensaje": "Demasiado bajo. Intenta de nuevo.", "intentos": intentos, "terminado": False}

    if numero > numero_secreto:
        return {"mensaje": "Demasiado alto. Intenta de nuevo.", "intentos": intentos, "terminado": False}

    return {
        "mensaje": f"Felicidades. Adivinaste el numero en {intentos} intentos.",
        "intentos": intentos,
        "terminado": True,
    }


@app.get("/api/reiniciar")
async def reiniciar_juego(request: Request):
    iniciar_juego(request)
    return {"mensaje": "Juego reiniciado. Adivina el numero entre 1 y 100.", "intentos": 0}