from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def formulario_triangulo():
    return """
    <html>
        <head>
            <title>Area de triangulo</title>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
        </head>
        <body class="min-h-screen bg-gradient-to-br from-amber-100 via-orange-50 to-red-100 flex items-center justify-center p-6">
            <main class="w-full max-w-md rounded-2xl bg-white/90 shadow-xl ring-1 ring-black/5 backdrop-blur p-8">
                <h1 class="text-3xl font-bold tracking-tight text-slate-900 mb-2">Calcular area de triangulo</h1>
                <p class="text-sm text-slate-600 mb-6">Ingresa la base y la altura para calcular el area.</p>
                <form id="triangulo-form" action="/triangulo" method="get" class="space-y-5">
                    <div>
                        <label for="base" class="block text-sm font-medium text-slate-700 mb-1">Base</label>
                        <input type="number" id="base" name="base" step="any" required class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-orange-400 focus:border-orange-400" placeholder="Ej. 10">
                    </div>
                    <div>
                        <label for="altura" class="block text-sm font-medium text-slate-700 mb-1">Altura</label>
                        <input type="number" id="altura" name="altura" step="any" required class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-orange-400 focus:border-orange-400" placeholder="Ej. 8">
                    </div>
                    <button type="submit" class="w-full rounded-lg bg-slate-900 text-white py-2.5 font-semibold hover:bg-slate-800 transition">Calcular</button>
                    <div id="resultado" class="mt-4 text-center text-lg font-medium text-slate-700"></div>
                </form>
            </main>
            <script>
                const form = document.getElementById("triangulo-form");
                const resultado = document.getElementById("resultado");

                form.addEventListener("submit", async (event) => {
                    event.preventDefault();

                    const base = form.base.value;
                    const altura = form.altura.value;

                    try {
                        const response = await fetch(`/triangulo?base=${encodeURIComponent(base)}&altura=${encodeURIComponent(altura)}`);
                        if (!response.ok) {
                            throw new Error("No se pudo calcular el area.");
                        }

                        const data = await response.json();
                        resultado.textContent = `El area del triangulo es: ${data.area}`;
                    } catch (error) {
                        resultado.textContent = "Ocurrio un error al calcular el area.";
                    }
                });
            </script>
        </body>
    </html>
    """

@app.get("/triangulo")
async def calcular_area_triangulo(base: float, altura: float):
    area = (base * altura) / 2
    return {"area": area}