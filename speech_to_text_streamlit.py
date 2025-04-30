import base64
import io
import streamlit as st
from audiorecorder import audiorecorder
from gtts import gTTS
from IPython.display import Audio
import speech_recognition as sr
import openai
import pyttsx3
import time
from tempfile import NamedTemporaryFile
import os

# Configure OpenAI API key
openai.api_key = st.secrets["OPEN_API_KEY"]

# Initialize pyttsx3 engine
# engine = pyttsx3.init()

def record_audio_source():
    """
    Records audio using the AudioRecorder component and saves it to 'audio.wav'.
    """
    audio = audiorecorder("Click to record", "Click to stop recording")
    if len(audio) > 0:
        # To play audio in frontend:
        st.audio(audio.export().read())

        # To save audio to a file, use pydub export method:
        audio.export("audio.wav", format="wav")

        # To get audio properties, use pydub AudioSegment properties:
        st.write(f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds")

        return "audio.wav"
    return "audio.wav"

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

# Function to convert text to speech
def text_to_speech(text):
    tts = gTTS(text, lang='en')
    tts.save("output.mp3")
    return "output.mp3"

def text_speech(text):
    tts = gTTS(text=text, lang='en')
    speech_bytes = io.BytesIO()
    tts.write_to_fp(speech_bytes)
    speech_bytes.seek(0)

    b64 = base64.b64encode(speech_bytes.read()).decode()
    if True:
        md = f"""
            <audio id="audioTag" controls autoplay>
            <source src="data:audio/mp3;base64,{b64}"  type="audio/mpeg" format="audio/mpeg">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    tts = None
    return b64

st.title("Eric's Mental Health SPEECH-BOT")
st.subheader("Hi there! Please speak about your mental health, such as your thoughts and feelings."
             " My speechbot is here to listen and Guide you.")

if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# with st.sidebar:
#     with st.echo():
#         st.write("This code will be printed to the sidebar.")
# 
#     with st.spinner("Loading..."):
#         time.sleep(5)
#     st.success("Done!")

audio = audiorecorder("Click to Speak", "Click to STOP Speaking")
# Record audio using the AudioRecorder component
# filename = record_audio_source()
if len(audio) > 0:
    # To play audio in frontend:
    st.audio(audio.export().read())

    # To save audio to a file, use pydub export method:
    filename = audio.export("audio.wav", format="wav")

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
    text_speech(st.session_state.conversation[-1][1])
