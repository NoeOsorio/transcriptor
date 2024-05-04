
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

def create_script(text: str):
    print("Creando script...")
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres experta en entender e interpretar una idea y convertirla en un script que enganche a miles de personas. Mejora la claridad y legibilidad de este texto, corrige redundania, basandote en su contexto. Manten el miso tono e intencion del narrador. Despues, como output, crea un script cinematografico inspirador que sea un monologo o narracion donde pueda hablar entre 1 y 2 minutos maximo con el siguiente texto:"},
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
