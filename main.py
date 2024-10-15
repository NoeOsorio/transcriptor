import argparse
import re
import os
from tqdm import tqdm
from audio_processing import divide_audio, eliminar_fragmentos
from file_handling import seleccionar_audio, seleccionar_acciones, crear_directorios
from gpt import voice_transcription, create_script, extract_key_points

# Configuración de argumentos
parser = argparse.ArgumentParser(
    description="Procesador de audio para scripts, transcripciones y resúmenes.")
parser.add_argument("-s", "--script", action="store_true",
                    help="Crea solo el script sin realizar la transcripción.")
parser.add_argument("-t", "--transcript", action="store_true",
                    help="Realiza solo la transcripción sin crear el script.")
parser.add_argument('--tone', type=str,
                    help='Tipo de tono del video. Ejemplo: Inspirador, motivacional, etc.', default="Inspirador")
parser.add_argument('--audio', type=str,
                    help='Nombre del archivo de audio', default="")
parser.add_argument('--resumen', type=str,
                    help='Resumen del video', default="")
parser.add_argument('-d', '--duracion', type=int,
                    help='Duración del video en minutos', default=2)
parser.add_argument('-k', '--keypoints', action="store_true",
                    help="Extrae los puntos clave del video.")

args = parser.parse_args()

# Si no se especifica una acción (-s, -t o -k), mostrar un menú seleccionable
if not any([args.script, args.transcript, args.keypoints]):
    acciones = seleccionar_acciones()
    args.script = 'script' in acciones
    args.transcript = 'transcript' in acciones
    args.keypoints = 'keypoints' in acciones

# Si no se especifica un archivo de audio, mostrar una lista seleccionable
if not args.audio:
    nombre_del_archivo = seleccionar_audio().replace(".m4a", "")
else:
    nombre_del_archivo = args.audio

# Limpiar el nombre del archivo
nombre_del_archivo = re.sub(r'[\\/*?:"<>|]', "", nombre_del_archivo)
audio_file = f"voice_notes/{nombre_del_archivo}.m4a"
text_file = f"transcriptions/{nombre_del_archivo}.txt"
ai_text_file = f"ai_text_notes/{nombre_del_archivo}.txt"

# Crear directorios si no existen
crear_directorios([text_file, ai_text_file])
segment_files: list = []
try:
    # Comprobar si el archivo de transcripción ya existe
    if args.transcript or not os.path.exists(text_file):
        print("Transcribiendo...")
        segment_files = divide_audio(audio_file)

        # Transcribir cada segmento y mostrar la barra de progreso
        with tqdm(total=len(segment_files), desc="Progreso de Transcripción") as pbar:
            for segment_file in segment_files:
                original_text = voice_transcription(segment_file)
                with open(text_file, "a", encoding='utf-8') as file:
                    file.write(original_text)
                pbar.update(1)
        print(f"Texto original guardado en archivo: {text_file}")
    else:
        print(f"El archivo de transcripción {
              text_file} ya existe. Omite la transcripción para ahorrar recursos.")

    # Comprobar si el archivo de script ya existe
    if args.script or not os.path.exists(ai_text_file):
        print("Creando script...")
        with open(text_file, 'r', encoding='utf-8') as file:
            original_text = file.read()
        ai_text = create_script(original_text, args.tone, args.duracion)
        with open(ai_text_file, "w", encoding='utf-8') as file:
            file.write(ai_text)
        print(f"Texto con AI guardado en archivo: {ai_text_file}")
    else:
        print(f"El archivo del script {
              ai_text_file} ya existe. Omite la creación de script para ahorrar recursos.")

    # Si se solicitó extraer puntos clave
    if args.keypoints:
        print("Extrayendo puntos clave...")
        with open(text_file, 'r', encoding='utf-8') as file:
            original_text = file.read()
        key_points = extract_key_points(original_text)
        resumen_file = f"keypoints/{nombre_del_archivo}_keypoints.md"
        crear_directorios([resumen_file])
        with open(resumen_file, "w", encoding='utf-8') as file:
            file.write(key_points)
        print(f"Puntos clave guardados en archivo: {resumen_file}")

    # Eliminar fragmentos de audio después de la transcripción
    eliminar_fragmentos(segment_files)

except Exception as e:
    print(f"Error: {e}")
