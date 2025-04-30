import streamlit as st
import sounddevice as sd
import wavio
import speech_recognition as sr
import openai
import pyttsx3
import time
from tempfile import NamedTemporaryFile
import os

# Configure OpenAI API key
openai.api_key = st.secrets["OPEN_API_KEY"]
# Initialize pyttsx3 engine
engine = pyttsx3.init()

def record_audio(record_seconds=5, rate=44100, device=0):
    """
    Records audio from the microphone and returns the filename.
    """
    with NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        filename = temp_audio_file.name
        print("Recording...")
        myrecording = sd.rec(int(record_seconds * rate), samplerate=rate, channels=1, device=device)
        sd.wait()  # Wait until recording is finished
        print("Finished recording.")
        wavio.write(filename, myrecording, rate, sampwidth=2)
    return filename

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

def query_chatgpt(prompt):
    """
    Queries the OpenAI ChatGPT API with the provided prompt.
    """
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",  # or "text-davinci-003" based on your available engines
        prompt=prompt,
        max_tokens=150
    )
    message = response.choices[0].text.strip()
    print("ChatGPT Response: " + message)
    return message

def speak_text(text):
    """
    Uses pyttsx3 to convert text to speech.
    """
    engine.say(text)
    engine.runAndWait()

st.title("Mental Health Chatbot")

if 'conversation' not in st.session_state:
    st.session_state.conversation = []

device_id = 0  # Replace with the appropriate device ID from your list

if st.button("Speak"):
    # Record audio from the microphone
    filename = record_audio(record_seconds=5, device=device_id)

    # Transcribe the recorded audio
    text = transcribe_audio(filename)

    if text:
        st.session_state.conversation.append(("user", text))
        print(f"Session state USER is : {st.session_state.conversation}")

        # Query ChatGPT API
        response_from_gpt = query_chatgpt(text)
        st.session_state.conversation.append(("bot", response_from_gpt))
        print(f"Session state BOT is : {st.session_state.conversation}")

        # Speak out the response
        speak_text(response_from_gpt)

# Display the conversation
# breakpoint()
print("AAAAAAAA")
for speaker, message in st.session_state.conversation:
    print("BBBBBBBB")
    if speaker == "user":
        print("CCCCCCCC")
        #st.markdown(f"<div style='text-align: left; color: blue;'>{message}</div>", unsafe_allow_html=True)
        st.button(message)
    else:
        print("-C-C-C-C-C")
        #st.markdown(f"<div style='text-align: right; color: green;'>{message}</div>", unsafe_allow_html=True)
        st.button(message)
