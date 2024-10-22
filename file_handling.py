import os
import inquirer
from video import descargar_audio_youtube, convertir_video_a_mp3


def seleccionar_fuente_audio():
    opciones = [
        ('YouTube', 'youtube'),
        ('Archivo de video local', 'video_local'),
        ('Archivo de audio existente', 'audio_existente')
    ]

    preguntas = [
        inquirer.List('fuente',
                      message="¿De dónde quieres obtener el audio?",
                      choices=opciones,
                      ),
    ]

    respuesta = inquirer.prompt(preguntas)

    if respuesta['fuente'] == 'youtube':
        url = input("Introduce la URL del video de YouTube:  ")
        return descargar_audio_youtube(url)
    elif respuesta['fuente'] == 'video_local':
        videos = [f for f in os.listdir(
            "videos") if f.endswith(('.mp4', '.avi', '.mov'))]
        video_seleccionado = inquirer.list_input(
            "Selecciona un archivo de video", choices=videos)
        return convertir_video_a_mp3(os.path.join("videos", video_seleccionado))
    elif respuesta['fuente'] == 'audio_existente':
        audios = [f for f in os.listdir(
            "voice_notes") if f.endswith(('.mp3', '.m4a', '.wav'))]
        audio_seleccionado = inquirer.list_input(
            "Selecciona un archivo de audio", choices=audios)
        return os.path.join("voice_notes", audio_seleccionado)


def seleccionar_audio():
    archivos = [f for f in os.listdir("voice_notes/") if f.endswith(('.mp3', '.m4a', '.wav'))]
    if not archivos:
        print("No hay archivos de audio en la carpeta voice_notes.")
        exit(1)
    pregunta = inquirer.list_input(
        "Selecciona el archivo de audio:", choices=archivos)
    return pregunta


def seleccionar_acciones():
    preguntas = [
        inquirer.Checkbox(
            "acciones",
            message="¿Qué deseas hacer con el archivo de audio?",
            choices=[
                ("Transcribir el audio", 'transcript'),
                ("Generar script", 'script'),
                ("Extraer puntos clave", 'keypoints'),
                ("Guardar en Notion", 'notion')
            ],
        )
    ]
    respuesta = inquirer.prompt(preguntas)
    return respuesta['acciones']


def crear_directorios(paths):
    for path in paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
