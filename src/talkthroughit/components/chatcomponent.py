from streamlit_realtime_audio_recorder import audio_recorder
import streamlit as st
import base64
import io
from elevenlabs.client import ElevenLabs
import requests
import tempfile

elevenlabs = ElevenLabs(api_key=st.secrets["elevenlabs"]["api_key"])


def audioRecording():
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
                    print(transcription.text)
                    st.session_state.text_from_audio.append([transcription.text,False])
                    
            else:
                pass
        elif result.get("error"):
            st.error(f"Error: {result.get('error')}")


def chatComponent(room_info):
    if "gemini" not in st.session_state:
        st.session_state["gemini"] = "gemini-2.5-flash"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.subheader("Chat")
    message_container = st.container(height=300, border=True)

    with message_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        audioRecording()
    with col2:
        if st.button("Get a question", use_container_width=True):
            content = st.session_state.current_tab_data["content"]
            if st.session_state.current_tab_data["type"] == "code":
                good_enough, question = room_info.get_question(
                    "test", code_snippet=content
                )
            else:
                good_enough, question = room_info.get_question(
                    "test", whiteboard_image_b64=content
                )
            st.session_state.messages.append({"role": "assistant", "content": question})
            with message_container.chat_message("assistant"):
                message_container.markdown(question)
