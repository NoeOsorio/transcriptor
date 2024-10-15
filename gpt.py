import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "gpt-4o-mini"
api_key = os.getenv('OPENAI_API_KEY')
organization = os.getenv('OPENAI_ORGANIZATION')

client = OpenAI(organization=organization, api_key=api_key)

def create_script(text: str, tone: str, duracion: int = 2):
    """Genera un script cinematográfico a partir de un texto dado."""
    messages = [
        {
            "role": "system", 
            "content": f"Eres un experto en la creación de guiones cinematográficos. "
                       f"Tu tarea es transformar el siguiente texto en un guion con tono {tone}, "
                       f"que tenga una duración aproximada de {duracion} minutos. El guion debe tener: "
                       f"- Un inicio que enganche al espectador desde el primer momento. "
                       f"- Un desarrollo que mantenga el interés. "
                       f"- Un cierre impactante que deje al espectador con ganas de más. "
                       f"Por favor, utiliza un lenguaje claro, humano y cercano, sin redundancias."
        },
        {"role": "user", "content": text}
    ]
    completion = client.chat.completions.create(model=MODEL_NAME, messages=messages)
    return completion.choices[0].message.content

def voice_transcription(audio_file: str):
    """Realiza la transcripción del archivo de audio."""
    try:
        with open(audio_file, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="text",

            )
        # Aseguramos que la respuesta es un diccionario y obtenemos el campo 'text'
        return transcript['text'] if 'text' in transcript else transcript
    except Exception as e:
        print(f"Error al transcribir el audio: {e}")
        return ""


def extract_key_points(text: str):
    """Extrae puntos clave de una transcripción o conversación."""
    chunks = split_text(text, max_tokens=1500)
    messages = [
        {
            "role": "system", 
            "content": """
                Eres un experto en resumir transcripciones complejas de conversaciones o reuniones. 
                Tu tarea es analizar la siguiente transcripción y extraer:
                1. Un resumen claro del objetivo principal de la conversación.
                2. Una lista de los puntos clave más importantes, con explicaciones adicionales para mayor claridad.
                3. Si se discutieron acciones, estrategias o decisiones, priorízalas en los puntos clave.
                4. Haz un analisis de los objetivos de la conversacion y da al menos 5 propuestas profesionales como experto para los siguientes pasos (Independiente de lo que se haya hablado en la conversacion, es decir quiero los puntos que hablaron los involucrados y ademas tu opinion de experto).
                5. Proporciona conclusiones claras para que quien lea el resumen pueda tomar decisiones basadas en la información proporcionada.
                Mantén un tono profesional y directo. Evita agregar información irrelevante o redundante.
                
                Una un minimo de dos parrafos para cada punto, dale un formato claro y profesional y el formato de salida sera en MD.
                """
        }
    ]
    messages.extend([{"role": "user", "content": chunk} for chunk in chunks])
    completion = client.chat.completions.create(model=MODEL_NAME, messages=messages)
    return completion.choices[0].message.content

def split_text(text, max_tokens=1500):
    """Divide el texto en fragmentos más pequeños para procesar con el modelo."""
    words = text.split()
    chunks, chunk = [], []
    current_tokens = 0

    for word in words:
        current_tokens += 1
        chunk.append(word)
        if current_tokens >= max_tokens:
            chunks.append(' '.join(chunk))
            chunk = []
            current_tokens = 0

    if chunk:
        chunks.append(' '.join(chunk))

    return chunks
