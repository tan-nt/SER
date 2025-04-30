import streamlit as st
import speech_recognition as sr
import openai
import pyttsx3
import pyaudio
import time
from tempfile import NamedTemporaryFile
import os

# Configure OpenAI API key
openai.api_key = st.secrets["OPEN_API_KEY"]

# Initialize pyttsx3 engine
# engine = pyttsx3.init()

def record_audio(record_seconds=5):
    """
    Records audio from the microphone and returns the filename.
    """
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Recording...")
            audio_data = recognizer.record(source, duration=record_seconds)
            print("Finished recording.")

        with NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
            filename = temp_audio_file.name
            with open(filename, "wb") as f:
                f.write(audio_data.get_wav_data())
        return filename
    except OSError as e:
        st.error("No default input device available. Please ensure a microphone is connected.")
        return None

def transcribe_audio(filename):
    """
    Transcribes the given audio file using Google's speech recognition.
    """
    if filename is None:
        return None
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

def query_chatgpt(prompt):
    """
    Queries the OpenAI ChatGPT API with the provided prompt.
    """
    base_prompt = (
            "You are a helpful assistant specialized in mental health support. "
            "Your job is to provide advice, support, and information about mental health issues. "
            "You can address topics like stress, anxiety, depression, anger management, and general well-being. "
            "Please keep your responses focused on mental health and well-being.\n\n"
            "User: " + prompt + "\n"
                                "Assistant:"
    )

    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",  # or "text-davinci-003" based on your available engines
        prompt=base_prompt,
        max_tokens=2500
    )
    message = response.choices[0].text.strip()
    print("ChatGPT Response: " + message)
    return message

def speak_text(text):
    """
    Uses pyttsx3 to convert text to speech.
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine = None

st.title("Mental Health Chatbot")
st.subheader("Welcome! Please speak about your mental health, such as your thoughts and feelings. Our chatbot is here to listen and respond to you.")

if 'conversation' not in st.session_state:
    st.session_state.conversation = []

if st.button("Speak"):
    # Record audio from the microphone
    filename = record_audio(record_seconds=5)

    # Transcribe the recorded audio
    text = transcribe_audio(filename)

    if text:
        st.session_state.conversation.append(("user", text))

        # Query ChatGPT API
        response = query_chatgpt(text)
        st.session_state.conversation.append(("bot", response))

# Display the conversation
for speaker, message in st.session_state.conversation:
    if speaker == "user":
        with st.chat_message("user"):
            st.write(message)
    else:
        with st.chat_message("assistant"):
            st.write(message)

# Speak out the latest response
if st.session_state.conversation and st.session_state.conversation[-1][0] == "bot":
    speak_text(st.session_state.conversation[-1][1])
