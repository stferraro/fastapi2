const guessForm = document.getElementById("guessForm");
const guessInput = document.getElementById("guessInput");
const result = document.getElementById("result");
const attempts = document.getElementById("attempts");
const restartButton = document.getElementById("restartButton");


async function iniciarJuego() {
	const response = await fetch("/api/adivina");
	const data = await response.json();
	result.textContent = data.mensaje;
	result.className = "mt-3 text-center alert alert-info";
	attempts.textContent = `Intentos: ${data.intentos}`;
}


guessForm.addEventListener("submit", async (event) => {
	event.preventDefault();

	const numero = Number(guessInput.value);

	if (!Number.isInteger(numero) || numero < 1 || numero > 100) {
		result.textContent = "Ingresa un numero entero entre 1 y 100.";
		result.className = "mt-3 text-center alert alert-warning";
		return;
	}

	const response = await fetch(`/api/adivina/${numero}`);
	const data = await response.json();

	result.textContent = data.mensaje;
	result.className = data.terminado
		? "mt-3 text-center alert alert-success"
		: "mt-3 text-center alert alert-secondary";
	attempts.textContent = `Intentos: ${data.intentos}`;

	if (data.terminado) {
		guessInput.value = "";
	}
});


restartButton.addEventListener("click", async () => {
	const response = await fetch("/api/reiniciar");
	const data = await response.json();
	result.textContent = data.mensaje;
	result.className = "mt-3 text-center alert alert-info";
	attempts.textContent = `Intentos: ${data.intentos}`;
	guessInput.value = "";
	guessInput.focus();
});


iniciarJuego();