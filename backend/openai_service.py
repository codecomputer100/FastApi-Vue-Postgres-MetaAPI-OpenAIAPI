# test_chatgpt.py
from openai import OpenAI

# Crea el cliente (usa tu API key como variable de entorno o en el código)
client = OpenAI(api_key="apikey")

# Envía un prompt sencillo
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": "Eres un asistente útil."},
        {"role": "user", "content": "Hola, ¿me puedes confirmar que la conexión funciona?"}
    ]
)

print(response.choices[0].message.content)

