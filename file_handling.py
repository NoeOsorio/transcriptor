import os
import inquirer

def seleccionar_audio():
    archivos = [f for f in os.listdir("voice_notes/") if f.endswith(".m4a")]
    if not archivos:
        print("No hay archivos de audio en la carpeta voice_notes.")
        exit(1)
    pregunta = inquirer.list_input("Selecciona el archivo de audio:", choices=archivos)
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

