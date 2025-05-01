import streamlit as st
from util.audio import record_audio
from util.chat import google_gemini_generate_answer
from util.speech import transcribe_audio, speak_text


st.title("Speech Recognition Project")

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
        response_from_gpt = google_gemini_generate_answer(text)
        st.session_state.conversation.append(("bot", response_from_gpt))
        print(f"Session state BOT is : {st.session_state.conversation}")

        # Speak out the response
        speak_text(response_from_gpt)

# Display the conversation
# breakpoint()
for speaker, message in st.session_state.conversation:
    if speaker == "user":
        #st.markdown(f"<div style='text-align: left; color: blue;'>{message}</div>", unsafe_allow_html=True)
        st.button(message)
    else:
        #st.markdown(f"<div style='text-align: right; color: green;'>{message}</div>", unsafe_allow_html=True)
        st.button(message)
