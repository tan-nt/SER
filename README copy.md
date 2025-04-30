# Mental Health Speech Bot
## You can find the Hosted [Mental Health Speech ChatBOT HERE.](https://mental-health-speech-chatbot-v4.streamlit.app/)
Mental Health Speech Bot! This tool provides a supportive environment where you can talk about your mental health, share your thoughts and feelings, and receive guidance. The bot uses advanced speech recognition and natural language processing to understand your concerns and offer relevant advice.

## Features

- **Audio Recording**: Record your thoughts and feelings using the integrated audio recorder.
- **Speech-to-Text**: Convert your recorded speech into text for processing.
- **ChatGPT Integration**: Get responses from the OpenAI ChatGPT, specifically tuned for mental health support.
- **Text-to-Speech**: Listen to the bot's responses with natural-sounding speech.

## How to Use

1. **Start the Application**: Visit the hosted URL: [Mental Health Speech Bot](https://mental-health-speech-chatbot-v4.streamlit.app/)
2. **Record Your Audio**: Click the "Click to Speak" button to start recording your thoughts and feelings. Click the "Click to STOP Speaking" button to stop the recording.
3. **Transcription**: The bot will automatically transcribe your audio input.
4. **Receive Guidance**: The transcribed text will be sent to ChatGPT, and you will receive a response with supportive advice and information.
5. **Listen to the Response**: The bot's response will be converted to speech so you can listen to it.

## Technical Details

This project is built using the following technologies:

- **Streamlit**: For creating the web interface.
- **audiorecorder**: For recording audio from the user.
- **gTTS**: For text-to-speech conversion.
- **speech_recognition**: For converting speech to text.
- **openai**: For integrating with the OpenAI ChatGPT API.
- **pyttsx3**: For converting text to speech using offline TTS.

### Code Overview

Here are some important snippets and their explanations:

### Audio Recording

```python
def record_audio_source():
    """
    Records audio using the AudioRecorder component and saves it to 'audio.wav'.
    """
    audio = audiorecorder("Click to record", "Click to stop recording")
    if len(audio) > 0:
        st.audio(audio.export().read())
        audio.export("audio.wav", format="wav")
        st.write(f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds")
        return "audio.wav"
    return "audio.wav"
```

This function uses the `audiorecorder` component to record audio from the user. It exports the audio to a file named `audio.wav` and displays the audio properties. If recording is successful, it returns the filename.

### Speech-to-Text Conversion

```python
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
```

This function transcribes the recorded audio file into text using Google's Speech Recognition API. It handles errors in case the audio is not recognized or there is an issue with the service request.

### Querying ChatGPT

```python
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
        engine="gpt-3.5-turbo-instruct",
        prompt=base_prompt,
        max_tokens=2500
    )
    message = response.choices[0].text.strip()
    print("ChatGPT Response: " + message)
    return message
```

This function sends the transcribed text to the OpenAI ChatGPT API. The prompt is tailored to ensure the bot provides mental health support and advice. The response from ChatGPT is returned as a string.

### Text-to-Speech Conversion

```python
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
```

This function converts the text response from ChatGPT into speech using the `gTTS` library. It then encodes the speech as a base64 string and generates an HTML audio player to play the speech in the Streamlit app.

### Putting It All Together

```python
st.title("Eric's Mental Health SPEECH-BOT")
st.subheader("Hi there! Please speak about your mental health, such as your thoughts and feelings."
             " My speechbot is here to listen and guide you.")

if 'conversation' not in st.session_state:
    st.session_state.conversation = []

audio = audiorecorder("Click to Speak", "Click to STOP Speaking")
if len(audio) > 0:
    st.audio(audio.export().read())
    filename = audio.export("audio.wav", format="wav")
    text = transcribe_audio(filename)

    if text:
        st.session_state.conversation.append(("user", text))
        response = query_chatgpt(text)
        st.session_state.conversation.append(("bot", response))

for speaker, message in st.session_state.conversation:
    if speaker == "user":
        with st.chat_message("user"):
            st.write(message)
    else:
        with st.chat_message("assistant"):
            st.write(message)

if st.session_state.conversation and st.session_state.conversation[-1][0] == "bot":
    text_speech(st.session_state.conversation[-1][1])
```

This snippet ties everything together, creating the user interface and handling the entire interaction flow from recording audio, transcribing it, querying ChatGPT, and responding with synthesized speech. The conversation history is maintained in the Streamlit session state to provide a continuous chat experience.
