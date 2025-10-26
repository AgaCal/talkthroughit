from streamlit_realtime_audio_recorder import audio_recorder
import streamlit as st
import base64
import io
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import requests
import tempfile
from streamlit_float import *
import random

elevenlabs = ElevenLabs(api_key=st.secrets["elevenlabs"]["api_key"])

voices = [
    "JBFqnCBsd6RMkjVDRZzb",
]
def audioRecording():
    if "transcriptions" not in st.session_state:
        st.session_state.transcriptions = set()
    if "text_from_audio" not in st.session_state:
        st.session_state.text_from_audio = []
    result = audio_recorder(interval=50, threshold=-60, silenceTimeout=1000)
    if result:
        if result.get("status") == "stopped":
            audio_data = result.get(
                "audioData",
            )
            if audio_data:
                audio_bytes = base64.b64decode(audio_data)
                audio_data = io.BytesIO(audio_bytes)
                with tempfile.NamedTemporaryFile(
                    suffix=".webm", delete=False
                ) as tmp_webm:
                    tmp_webm.write(audio_bytes)
                    tmp_webm.flush()
                    transcription = elevenlabs.speech_to_text.convert(
                        file=audio_data,
                        model_id="scribe_v1",
                        tag_audio_events=True,
                        language_code="eng",
                        diarize=True,
                    )
                    if transcription.text in st.session_state.transcriptions:
                        return False
                    else:
                        st.session_state.transcription.add(transcription.text)
                    print(transcription.text)
                    audio_data = None
                    if len(transcription.text.split()) < 10: return False
                    st.session_state.text_from_audio.append([transcription.text, False])
                    return True
            else:
                pass
        elif result.get("error"):
            st.error(f"Error: {result.get('error')}")


def ask_a_question(room_info,message_container):
    content = st.session_state.current_tab_data["content"]
    context_message = ""
    for message,sent in st.session_state.text_from_audio:
        if not sent:
            context_message += message + '\n'
            sent = True
    if st.session_state.current_tab_data["type"] == "code":
        good_enough, question = room_info.get_question(
            context_message, code_snippet=content
        )
    else:
        good_enough, question = room_info.get_question(
            context_message, whiteboard_image_b64=content
        )

    st.session_state.messages.append({"role": "assistant", "content": question})
    audio = elevenlabs.text_to_speech.convert(
        text=question,
        voice_id=voices[random.randint(0,len(voices)-1)],
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
        voice_settings = {
            "speed": 1.1,
        }
    )
    with message_container.chat_message("assistant"):
        message_container.markdown(question)
    play(audio)

def chat(room_info):
    with st.container(key='main-chat-container',
                      border=False, vertical_alignment='distribute'):
        message_container = st.container(border=False, key='message-container', height='stretch')
        with message_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        with st.container(key='chat-bottom', border=False):
            if prompt := st.chat_input("Ask me anything...", key='chat-input'):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()

            with st.container(key='chat-buttons-container', border=False):
                if st.button("Get question", key='get-question-button'):
                    ask_a_question(room_info,message_container)
                elif audioRecording():
                    ask_a_question(room_info,message_container)


def chatComponent(room_info, room_id):
    random.seed(room_id)
    if "gemini" not in st.session_state:
        st.session_state["gemini"] = "gemini-2.5-flash"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    chat_container = st.container(height=600, border=True)
    with chat_container:
        chat(room_info)
