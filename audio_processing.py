import os
from pydub import AudioSegment

MAX_SEGMENT_SIZE = 25 * 1024 * 1024  # 25MB
TEN_MINUTES = 10 * 60 * 1000  # 10 minutos en milisegundos

def divide_audio(audio_file, max_size=MAX_SEGMENT_SIZE):
    print(f"Dividiendo el archivo de audio {audio_file} en segmentos...")
    audio = AudioSegment.from_file(audio_file)

    segments = []
    segment_duration_ms = TEN_MINUTES
    start_time = 0

    while start_time < len(audio):
        segment = audio[start_time:start_time + segment_duration_ms]
        while len(segment.raw_data) > max_size:
            segment_duration_ms = int(segment_duration_ms * 0.9)
            segment = audio[start_time:start_time + segment_duration_ms]

        segments.append(segment)
        start_time += segment_duration_ms

    segment_files = []
    os.makedirs("segments_audio", exist_ok=True)

    for idx, segment in enumerate(segments):
        segment_file = f"segments_audio/{os.path.basename(audio_file)}_segment_{idx}.wav"
        segment.export(segment_file, format="wav")
        segment_files.append(segment_file)

    print(f"Audio dividido en {len(segments)} segmentos.")
    return segment_files

def eliminar_fragmentos(segment_files):
    for segment_file in segment_files:
        try:
            os.remove(segment_file)
            print(f"Archivo {segment_file} eliminado correctamente.")
        except Exception as e:
            print(f"Error al eliminar {segment_file}: {e}")
