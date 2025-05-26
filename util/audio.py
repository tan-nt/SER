
import sounddevice as sd
import wavio
from util.config import cf

from tempfile import NamedTemporaryFile

print(sd.query_devices())

def record_audio(record_seconds=5, rate=44100, device=0):
    """
    Records audio from the microphone and returns the filename.
    """
    with NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        filename = temp_audio_file.name
        if cf.get("ENV") == "dev":
            # For local macos
            device = 0
        myrecording = sd.rec(int(record_seconds * rate), samplerate=rate, channels=1, device=device)
        sd.wait()  # Wait until recording is finished
        print("Finished recording.")
        wavio.write(filename, myrecording, rate, sampwidth=2)
    return filename