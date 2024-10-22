import os
import yt_dlp
from pydub import AudioSegment
import subprocess

# Función para descargar audio de YouTube usando yt-dlp
def descargar_audio_youtube(url, carpeta="voice_notes"):
    try:
        os.makedirs(carpeta, exist_ok=True)
        print(f"Descargando audio desde: {url}")

        # Configuración para descargar solo audio en formato mp3
        opciones = {
            'format': 'bestaudio/best',
            'outtmpl': f'{carpeta}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        # Descargar el audio
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=True)
            archivo_audio = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
        
        print(f"Audio descargado y convertido: {archivo_audio}")
        return archivo_audio

    except Exception as e:
        print(f"Error al descargar o convertir el audio: {e}")
        return None
    
def convertir_video_a_mp3(ruta_video, carpeta_salida="voice_notes"):
    try:
        os.makedirs(carpeta_salida, exist_ok=True)
        nombre_archivo = os.path.basename(ruta_video)
        nombre_base, _ = os.path.splitext(nombre_archivo)
        ruta_salida = os.path.join(carpeta_salida, f"{nombre_base}.mp3")

        print(f"Convirtiendo video a audio: {ruta_video}")

        # Usar FFmpeg directamente para convertir el video a audio MP3
        comando = [
            'ffmpeg',
            '-i', ruta_video,
            '-vn',  # No video
            '-acodec', 'libmp3lame',  # Codec de audio MP3
            '-b:a', '192k',  # Bitrate de audio
            '-y',  # Sobrescribir archivo de salida si existe
            ruta_salida
        ]

        resultado = subprocess.run(comando, capture_output=True, text=True)
        
        if resultado.returncode != 0:
            print(f"Error en FFmpeg: {resultado.stderr}")
            return None

        print(f"Video convertido a audio MP3: {ruta_salida}")
        return ruta_salida

    except Exception as e:
        print(f"Error al convertir el video a audio: {e}")
        return None

def descargar_video_youtube(url, carpeta="videos"):
    try:
        os.makedirs(carpeta, exist_ok=True)
        print(f"Descargando video desde: {url}")

        # Configuración para descargar video
        opciones = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'{carpeta}/%(title)s.%(ext)s',
        }

        # Descargar el video
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=True)
            archivo_video = ydl.prepare_filename(info)
        
        print(f"Video descargado: {archivo_video}")
        return archivo_video

    except Exception as e:
        print(f"Error al descargar el video: {e}")
        return None


# Ejemplo de uso
if __name__ == "__main__":
    url_video = input("Introduce la URL del video de YouTube: ")
    # archivo_audio = descargar_audio_youtube(url_video)
    archivo_video = descargar_video_youtube(url_video)
    convertir_video_a_mp3(archivo_video)
    # if archivo_audio:
    #     print(f"¡Audio guardado en: {archivo_audio}!")
