import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "gpt-4o-mini"

organization = os.getenv('OPENAI_ORGANIZATION')
project = os.getenv('OPENAI_PROYJECT')
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(
    organization=organization,
    project=project,
    api_key=api_key
)


def create_script(text: str, tone: str, duracion: int = 2):
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": """Eres experta en entender e interpretar una idea y 
             convertirla en un script que enganche a miles de personas. Mejora la claridad y legibilidad 
             de este texto, corrige redundancia, basándote en su contexto. Mantén el mismo tono e intención del narrador. 
             Utiliza lenguaje cotidiano y cercano (sin llegar a ser vulgar o irrespetuoso), sonando lo más humano posible."""},
            {"role": "system", "content": f"""
             Después, como output, crea un script cinematográfico con un tono {tone} que sea un monólogo o narración,
             donde pueda hablar aproximadamente {duracion} minutos con el siguiente texto. Recuerda que debe tener
             un inicio con un gancho, un desarrollo y un cierre que deje al espectador con ganas de más.
             """},
            {"role": "user", "content": text}
        ]
    )
    print("Script:")
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content


def voice_transcription(audio_file: str):
    try:
        print("Iniciando transcripción de audio...")
        with open(audio_file, "rb") as audio:
            print("Transcribiendo audio...")
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="text"
            )
        print("Transcripción del audio completada.")
        # Aseguramos que la respuesta es un diccionario y obtenemos el campo 'text'
        return transcript['text'] if 'text' in transcript else transcript
    except Exception as e:
        print(f"Error al transcribir el audio: {e}")
        return ""


# Función para dividir el texto en fragmentos pequeños
def split_text(text, max_tokens=1500):
    words = text.split()
    current_tokens = 0
    chunk = []
    chunks = []

    for word in words:
        current_tokens += 1  # Aproximamos cada palabra como un token
        chunk.append(word)
        if current_tokens >= max_tokens:
            chunks.append(' '.join(chunk))
            chunk = []
            current_tokens = 0

    if chunk:
        chunks.append(' '.join(chunk))

    return chunks

# Función para extraer puntos clave
def extract_key_points(text: str):
    print("Extrayendo puntos clave del texto...")
    text_chunks = split_text(text, max_tokens=1500)  # Dividir en fragmentos de máximo 1500 tokens

    # Construir los mensajes basados en los chunks de texto
    messages = [{"role": "system", "content": """
                    Cuando te proporcione una transcripción de una conversación, tu tarea será identificar primero el objetivo principal de la conversación y resumirlo en uno o dos parrafos. 
                    A continuación, extraerás los puntos más importantes de la discusión y los presentarás como una lista no ordenada, donde cada punto incluirá una explicación o contexto adicional para mayor claridad. 
                    Mantén un tono profesional y demuestra un nivel de maestría en la redacción, asegurándote de que el resumen sea claro, preciso y esté orientado a proporcionar información útil y accionable. 
                    Si la conversación involucra a múltiples personas, enfócate en extraer los puntos clave relacionados con las decisiones, estrategias o acciones acordadas, priorizando el contexto de la conversación.
                    Puedes extenderte lo necesario para que los puntos clave sean claros y comprensibles, pero evita agregar información irrelevante o redundante. Explica de forma extensa cada punto clave.
                    """}]
    
    # Agregar cada chunk como un mensaje del usuario
    messages.extend([{"role": "user", "content": chunk} for chunk in text_chunks])

    try:
        # Realizar la solicitud a OpenAI
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages
        )
        # Retornar el resultado del resumen
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error al procesar los chunks: {e}")
        return ""

