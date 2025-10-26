from streamlit_realtime_audio_recorder import audio_recorder
import streamlit as st
import base64
import io
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
speech_recognizer = sr.Recognizer()

def audioRecording():
    if "text_from_audio" not in st.session_state:
        st.session_state.text_from_audio = []
    result = audio_recorder(interval=50, threshold=-60, silenceTimeout=1000)
    if result:
        if result.get("status") == "stopped":
            audio_data = result.get("audioData",)
            if audio_data:
                audio_bytes = base64.b64decode(audio_data)
                with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp_webm:
                    tmp_webm.write(audio_bytes)
                    tmp_webm.flush()
                    tmp_webm_path = tmp_webm.name
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
                    audio_pydub = AudioSegment.from_file(tmp_webm_path)
                    audio_pydub.export(tmp_wav.name, format="wav")  # export to filename
                    tmp_wav.flush()
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(tmp_wav.name) as source:
                        audio_data = recognizer.record(source)  # <-- record the audio from the file
                        text = recognizer.recognize_sphinx(audio_data)
                        st.session_state.text_from_audio.append([text,False])
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
            if st.session_state.current_tab_data["type"] == "code":
                code = st.session_state.current_tab_data["content"]
                good_enough,question = question = room_info.get_question("test",code_snippet=code)
            else:
                good_enough,question = question = room_info.get_question("test",)
            st.session_state.messages.append({"role": "assistant", "content": question})
            with message_container.chat_message("assistant"):
                message_container.markdown(question)
        
        
