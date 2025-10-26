from streamlit_realtime_audio_recorder import audio_recorder
import streamlit as st
import base64
import io
import speech_recognition as sr
from pydub import AudioSegment
speech_recognizer = sr.Recognizer()

def audioRecording():
    result = audio_recorder(interval=50, threshold=-60, silenceTimeout=1000)
    if result:
        if result.get("status") == "stopped":
            audio_data = result.get("audioData",)
            if audio_data:
                audio_bytes = base64.b64decode(audio_data)
                webm_buffer = io.BytesIO(audio_bytes)
                st.audio(webm_buffer,format="audio/webm")
                audio_pydub = AudioSegment.from_file(webm_buffer, format="webm")
                wav_buffer = io.BytesIO()
                audio_pydub.export(wav_buffer, format="wav")
                with sr.AudioFile(wav_buffer) as source:
                    speech_recognizer.recognize_sphinx(source)
            else:
                pass
        elif result.get("error"):
            st.error(f"Error: {result.get('error')}")
def ask_me():
    pass


def chatComponent(room_info):
    if "gemini" not in st.session_state:
        st.session_state["gemini"] = "gemini-2.5-flash"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    message_container = st.container(height=380)

    with message_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with message_container.chat_message("user"):
            message_container.markdown(prompt)
    record, ask, emtpty = st.columns([1, 1, 2])
    with record:
        audioRecording()
    with ask:
        question_button = st.button(label="",icon=":material/question_mark:")
        if question_button:
            question = room_info.get_question("test")
            st.session_state.messages.append({"role": "assistant", "content": question})
            with message_container.chat_message("assistant"):
                message_container.markdown(question)
        
        
