import random
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from scalar_fastapi import get_scalar_api_reference
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(
    title="Adivina Numero 2 API",
    description="Aplicacion FastAPI con Jinja para el juego de adivinar el numero.",
    version="1.0.0",
)
app.add_middleware(SessionMiddleware, secret_key="adivina-numero2-jinja")

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR))


def iniciar_juego(request: Request):
    request.session["numero_secreto"] = random.randint(1, 100)
    request.session["intentos"] = 0


def contexto_base(request: Request, **extra):
    contexto = {
        "request": request,
        "mensaje": "Intenta adivinar el numero entre 1 y 100.",
        "intentos": request.session.get("intentos", 0),
        "numero_ingresado": "",
        "terminado": False,
    }
    contexto.update(extra)
    return contexto


@app.get("/")
async def formulario(request: Request):
    if "numero_secreto" not in request.session:
        iniciar_juego(request)

    return templates.TemplateResponse(
        request,
        "index.html",
        contexto_base(request),
    )


@app.post("/intentar")
async def intentar_numero(request: Request, numero: int = Form(...)):
    if "numero_secreto" not in request.session:
        iniciar_juego(request)

    if numero < 1 or numero > 100:
        return templates.TemplateResponse(
            request,
            "index.html",
            contexto_base(
                request,
                mensaje="Ingresa un numero entre 1 y 100.",
                numero_ingresado=numero,
            ),
            status_code=400,
        )

    numero_secreto = request.session["numero_secreto"]
    intentos = request.session.get("intentos", 0) + 1
    request.session["intentos"] = intentos

    if numero < numero_secreto:
        mensaje = "Demasiado bajo. Intenta de nuevo."
        terminado = False
    elif numero > numero_secreto:
        mensaje = "Demasiado alto. Intenta de nuevo."
        terminado = False
    else:
        mensaje = f"Felicidades. Adivinaste el numero en {intentos} intentos."
        terminado = True

    return templates.TemplateResponse(
        request,
        "index.html",
        contexto_base(
            request,
            mensaje=mensaje,
            intentos=intentos,
            numero_ingresado=numero,
            terminado=terminado,
        ),
    )


@app.post("/reiniciar")
async def reiniciar(request: Request):
    iniciar_juego(request)
    return RedirectResponse(url="/", status_code=303)


@app.get("/scalar", include_in_schema=False)
async def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Adivina Numero 2 - Scalar",
    )