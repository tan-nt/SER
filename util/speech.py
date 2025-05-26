

import speech_recognition as sr
import pyttsx3
import threading

def transcribe_audio(filename):
    """
    Transcribes the given audio file using Google's speech recognition.
    """
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(filename)

    with audio_file as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        print("Transcription: " + text)
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

import pyttsx3
from multiprocessing import Process

def _speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def speak_text(text):
    p = Process(target=_speak, args=(text,))
    p.start()