import os
import re
from gpt import voice_transcription, create_script
import argparse

# Crea el parser
parser = argparse.ArgumentParser(
    description="Procesador de audio para scripts y transcripciones.")
parser.add_argument("-s", "--script", action="store_true",
                    help="Crea solo el script sin realizar la transcripción.")
parser.add_argument("-t", "--transcript", action="store_true",
                    help="Realiza solo la transcripción sin crear el script.")
parser.add_argument('--tone', type=str,
                    help='Tipo de tono del video. Ejemplo: Inspirador, motivacional, etc.', default="Inspirador")
parser.add_argument('--audio', type=str, help='Nombre del archivo de audio', default="")
parser.add_argument('--resumen', type=str, help='Resumen del video', default="")
parser.add_argument('-d', '--duracion', type=int,
                    help='Duración del video en minutos', default=2)

# Parsea los argumentos
args = parser.parse_args()

print(args)
# Variables
if(args.audio):
    nombre_del_archivo = args.audio
else:
    nombre_del_archivo = input("Nombre del archivo: ")
# Limpia el nombre del archivo
nombre_del_archivo = re.sub(r'[\\/*?:"<>|]', "", nombre_del_archivo)
audio_file = f"voice_notes/{nombre_del_archivo}.m4a"
text_file = f"text_notes/{nombre_del_archivo}.txt"
ai_text_file = f"ai_text_notes/{nombre_del_archivo}.txt"

# Crear directorio si no existe
os.makedirs(os.path.dirname(text_file), exist_ok=True)
os.makedirs(os.path.dirname(ai_text_file), exist_ok=True)


try:
    if args.transcript:
        print("Transcribiendo... ")
        # Mostrar loader
        print("Reconociendo... ")
        # Inicializar el reconocimiento de voz
        original_text = voice_transcription(audio_file)
        # Guardar el texto en un archivo
        with open(text_file, "w", encoding='utf-8') as file:
            file.write(original_text)
        print(f"Texto original guardado en archivo: {text_file}")
    elif args.script:
        print("Creando script... ")
        original_text = ""
        with open(text_file, 'r', encoding='utf-8') as file:
            original_text = file.read()
        ai_text = create_script(original_text, args.tone, args.duracion)
        with open(ai_text_file, "w", encoding='utf-8') as file:
            file.write(ai_text)
        print(f"Texto con ai guardado en archivo: {text_file}")
    else:
        # Mostrar loader
        print("Reconociendo... ")
        # Inicializar el reconocimiento de voz
        original_text = voice_transcription(audio_file)
        # Guardar el texto en un archivo
        with open(text_file, "w", encoding='utf-8') as file:
            file.write(original_text)
        print(f"Texto original guardado en archivo: {text_file}")
        ai_text = create_script(original_text, args.tone, args.duracion)
        with open(ai_text_file, "w", encoding='utf-8') as file:
            file.write(ai_text)
        print(f"Texto con ai guardado en archivo: {text_file}")
except Exception as e:
    print(f"Error: {e}")
