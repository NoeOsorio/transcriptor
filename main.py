import os
import re
from gpt import voice_transcription, create_script, extract_key_points
import argparse
from pydub import AudioSegment
from tqdm import tqdm  # Importar tqdm para la barra de progreso
import inquirer  # Para la selección de archivos interactivos

# Tamaño máximo de segmento en bytes (25MB)
MAX_SEGMENT_SIZE = 25 * 1024 * 1024
TEN_MINUTES = 10 * 60 * 1000  # 10 minutos en milisegundos

# Función para dividir el audio en segmentos pequeños (menos de 25 MB)


def divide_audio(audio_file, max_size=MAX_SEGMENT_SIZE):  # max_size en bytes (25MB)
    print(f"Dividiendo el archivo de audio {audio_file} en segmentos...")
    audio = AudioSegment.from_file(audio_file)

    # Duración aproximada para un segmento de tamaño adecuado (ajustar si es necesario)
    segment_duration_ms = TEN_MINUTES  # Comienza con 10 minutos en milisegundos
    segments = []
    start_time = 0

    while start_time < len(audio):
        segment = audio[start_time:start_time + segment_duration_ms]

        # Si el tamaño del segmento es mayor que max_size, reduce la duración
        while len(segment.raw_data) > max_size:
            # Reduce un 10% la duración
            segment_duration_ms = int(segment_duration_ms * 0.9)
            segment = audio[start_time:start_time + segment_duration_ms]

        segments.append(segment)
        start_time += segment_duration_ms

    segment_files = []
    os.makedirs("segments_audio", exist_ok=True)

    # Exportar los segmentos a archivos
    for idx, segment in enumerate(segments):
        segment_file = f"segments_audio/{nombre_del_archivo}_segment_{idx}.wav"
        segment.export(segment_file, format="wav")
        segment_files.append(segment_file)

    print(f"Audio dividido en {len(segments)} segmentos.")
    return segment_files

# Función para eliminar los fragmentos de audio
def eliminar_fragmentos(segment_files):
    for segment_file in segment_files:
        try:
            os.remove(segment_file)
            print(f"Archivo {segment_file} eliminado correctamente.")
        except Exception as e:
            print(f"Error al eliminar {segment_file}: {e}")

# Función para seleccionar un archivo de audio de la carpeta voice_notes
def seleccionar_audio():
    archivos = [f for f in os.listdir("voice_notes/") if f.endswith(".m4a")]
    
    if not archivos:
        print("No hay archivos de audio en la carpeta voice_notes.")
        exit(1)
    
    preguntas = [
        inquirer.List(
            "archivo",
            message="Selecciona el archivo de audio",
            choices=archivos,
        )
    ]
    respuesta = inquirer.prompt(preguntas)
    return respuesta["archivo"]

def seleccionar_acciones():
    preguntas = [
        inquirer.Checkbox(
            "acciones",
            message="¿Qué deseas hacer con el archivo de audio?",
            choices=[
                ("Transcribir el audio", 'transcript'),
                ("Generar script", 'script'),
                ("Extraer puntos clave", 'keypoints')
            ],
        )
    ]
    
    respuesta = inquirer.prompt(preguntas)
    return respuesta['acciones']



# Crea el parser
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

# Parsea los argumentos
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

# Limpia el nombre del archivo
nombre_del_archivo = re.sub(r'[\\/*?:"<>|]', "", nombre_del_archivo)
audio_file = f"voice_notes/{nombre_del_archivo}.m4a"
text_file = f"transcriptions/{nombre_del_archivo}.txt"
ai_text_file = f"ai_text_notes/{nombre_del_archivo}.txt"

# Crear directorios si no existen
os.makedirs(os.path.dirname(text_file), exist_ok=True)
os.makedirs(os.path.dirname(ai_text_file), exist_ok=True)

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
                pbar.update(1)  # Actualizar la barra de progreso
        print(f"Texto original guardado en archivo: {text_file}")
    else:
        print(f"El archivo de transcripción {text_file} ya existe. Omite la transcripción para ahorrar recursos.")

    # Comprobar si el archivo de script ya existe
    if args.script or not os.path.exists(ai_text_file):
        print("Creando script...")
        original_text = ""
        with open(text_file, 'r', encoding='utf-8') as file:
            original_text = file.read()
        ai_text = create_script(original_text, args.tone, args.duracion)
        with open(ai_text_file, "w", encoding='utf-8') as file:
            file.write(ai_text)
        print(f"Texto con AI guardado en archivo: {ai_text_file}")
    else:
        print(f"El archivo del script {ai_text_file} ya existe. Omite la creación de script para ahorrar recursos.")

    # Si se solicitó extraer puntos clave
    if args.keypoints:
        print("Extrayendo puntos clave...")
        with open(text_file, 'r', encoding='utf-8') as file:
            original_text = file.read()
        key_points = extract_key_points(original_text)
        resumen_file = f"keypoints/{nombre_del_archivo}_keypoints.md"
        os.makedirs(os.path.dirname(resumen_file), exist_ok=True)
        with open(resumen_file, "w", encoding='utf-8') as file:
            file.write(key_points)
        print(f"Puntos clave guardados en archivo: {resumen_file}")

    # Eliminar fragmentos de audio después de la transcripción
    eliminar_fragmentos(segment_files)

except Exception as e:
    print(f"Error: {e}")