
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

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
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": """Eres experta en entender e interpretar una idea y 
             convertirla en un script que enganche a miles de personas. 
             Mejora la claridad y legibilidad de este texto, corrige redundania, basandote en su contexto. 
             Manten el miso tono e intencion del narrador. Utiliza lenguaje cotidiano y cercano (sin llegar a ser vulgar o irrespetuoso)
             sonando lo más humano posible."""},
            {"role": "system", "content": f"""
             Despues, como output, crea un script cinematografico con un tono {tone} que sea un monologo
             o narracion donde pueda hablar aproximadamente {duracion} minutos con el siguiente texto. Recuerda que debe tener
             un inicio con un gancho, un desarrollo y un cierre que deje al espectador con ganas de más.
             """},
            {"role": "user", "content": text}
        ]
    )
    print("Script:")
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content


def voice_transcription(audio_file: str):
    print("Iniciando transcripción de audio...")
    audio_file = open(audio_file, "rb")
    print("Transcribiendo audio...")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    print("Transcripción del audio:")
    print(transcript)
    return transcript.text
