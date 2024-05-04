import os
import re
import speech_recognition as sr
from pydub import AudioSegment
from gpt import mejorar_texto

# Variables
nombre_del_archivo = "Programar es para todos?"
nombre_del_archivo = re.sub(r'[\\/*?:"<>|]', "", nombre_del_archivo)  # Limpia el nombre del archivo
audio_file = f"voice_notes/{nombre_del_archivo}.m4a"
wav_file = f"voice_notes/{nombre_del_archivo}.wav"
text_file = f"text_notes/{nombre_del_archivo}.txt"
ai_text_file = f"ai_text_notes/{nombre_del_archivo}.txt"

# Crear directorio si no existe
os.makedirs(os.path.dirname(text_file), exist_ok=True)

# Convierte M4A a WAV
print("Convirtiendo audio...")
audio = AudioSegment.from_file(audio_file, format="m4a")
audio.export(wav_file, format="wav")

# Usar archivo WAV con speech_recognition
print("Procesando reconocimiento de voz...")
r = sr.Recognizer()
with sr.AudioFile(wav_file) as source:
    audio = r.record(source)  # lee todo el archivo

try:
    # Mostrar loader
    print("Reconociendo... ")
    
    text = r.recognize_google(audio, language="es-MX")
    print("\nTexto reconocido")

    # Guardar el texto en un archivo
    with open(text_file, "w", encoding='utf-8') as file:
        file.write(text)
    print(f"Texto guardado en archivo: {text_file}")
    
    ai_text = mejorar_texto(text)
    
    with open(ai_text_file, "w", encoding='utf-8') as file:
        file.write(ai_text)
    print(f"Texto guardado en archivo: {text_file}")

except sr.UnknownValueError:
    print("Google Speech Recognition no pudo entender el audio")
except sr.RequestError as e:
    print(f"No se pudo solicitar resultados del servicio de reconocimiento de voz de Google; {e}")
except Exception as e:
    print(f"Error: {e}")
