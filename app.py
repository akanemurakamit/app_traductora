from flask import Flask, render_template, request
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Crear aplicación Flask
app = Flask(__name__)

# Modelo Qwen2-0.5B-Instruct de Hugging Face
MODEL_NAME = "Qwen/Qwen2-0.5B-Instruct"

print("Cargando modelo... Esto puede tardar la primera vez.")

# Cargar tokenizer y modelo
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto",
    device_map="auto"
)

print("Modelo cargado correctamente.")


def traducir_ingles_a_espanol(texto):
    """
    Función que recibe una frase en inglés
    y devuelve su traducción al español usando Qwen2-0.5B.
    """

    messages = [
        {
            "role": "system",
            "content": "Eres un traductor profesional. Traduce del inglés al español. Responde únicamente con la traducción, sin explicaciones."
        },
        {
            "role": "user",
            "content": f"Traduce esta frase al español: {texto}"
        }
    ]

    # Crear prompt en formato chat
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # Tokenizar entrada
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    # Generar respuesta
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=80,
            temperature=0.2,
            do_sample=True,
            top_p=0.9
        )

    # Obtener solo los tokens nuevos generados por el modelo
    generated_ids = outputs[0][inputs["input_ids"].shape[-1]:]

    respuesta = tokenizer.decode(
        generated_ids,
        skip_special_tokens=True
    ).strip()

    return respuesta


@app.route("/", methods=["GET", "POST"])
def index():
    traduccion = ""
    texto_original = ""

    if request.method == "POST":
        texto_original = request.form.get("texto", "")

        if texto_original.strip():
            traduccion = traducir_ingles_a_espanol(texto_original)

    return render_template(
        "index.html",
        texto_original=texto_original,
        traduccion=traduccion
    )


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
