import os
import re
from gpt import voice_transcription, create_script

# Variables
nombre_del_archivo = "Programar es para todos?"
# Limpia el nombre del archivo
nombre_del_archivo = re.sub(r'[\\/*?:"<>|]', "", nombre_del_archivo)
audio_file = f"voice_notes/{nombre_del_archivo}.m4a"
text_file = f"text_notes/{nombre_del_archivo}.txt"
ai_text_file = f"ai_text_notes/{nombre_del_archivo}.txt"

# Crear directorio si no existe
os.makedirs(os.path.dirname(text_file), exist_ok=True)
os.makedirs(os.path.dirname(ai_text_file), exist_ok=True)


try:
    # Mostrar loader
    print("Reconociendo... ")
    # Inicializar el reconocimiento de voz
    original_text = voice_transcription(audio_file)
    
    # Guardar el texto en un archivo
    with open(text_file, "w", encoding='utf-8') as file:
        file.write(original_text)
    print(f"Texto original guardado en archivo: {text_file}")

    ai_text = create_script(original_text)

    with open(ai_text_file, "w", encoding='utf-8') as file:
        file.write(ai_text)
    print(f"Texto con ai guardado en archivo: {text_file}")
except Exception as e:
    print(f"Error: {e}")
