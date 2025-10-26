import streamlit as st
from streamlit_router import StreamlitRouter
from talkthroughit.rooms.room import create_room, get_room
from components.room import room_page

def landing_page() -> None:
    st.set_page_config(page_title="talkthrough.it — create session")
    st.title("talkthrough.it — create a session")

    st.markdown(
        "Enter a topic and upload one or more files to create a session."
    )

    topic = st.text_input("Topic", value="")

    uploaded = st.file_uploader(
        "Upload files (pdf)", accept_multiple_files=True, type=['pdf'])

    if st.button("Create session"):
        if not topic:
            st.error("Please enter a topic before creating a session.")
            return

        if not uploaded:
            st.error("Please upload at least one file.")
            return

        # Read uploaded files into (filename, bytes) tuples
        documents: list[tuple[str, bytes]] = []
        for f in uploaded:
            try:
                data = f.read()
            except Exception as e:
                st.error(f"Failed to read file {f.name}: {e}")
                return
            documents.append((f.name, data))

        with st.spinner("Creating session and processing documents..."):
            room_id = create_room(topic, documents)

        st.success(f"Room created: {room_id}")
        st.write("Topic:", topic)
        st.write("Files:", [n for n, _ in documents])

        # Persist room_id in session state for QA step
        st.session_state.room_id = room_id
        session_page = router.build("room_page",{"session_id" : room_id})
        router.redirect(*session_page)
    # QA step after room creation
    if "room_id" in st.session_state:
        room_id = st.session_state.room_id
        room = get_room(room_id)

        st.header("Explain the topic and get a question")
        explanation = st.text_area("Explain the topic:", key="explanation")

        if st.button("Ask me a question"):
            if not explanation.strip():
                st.error("Please provide an explanation before "
                         "asking for a question.")
                return

            inputs = {
                "topic": room.topic,
                "input": explanation,
                # "whiteboard_image": "",  # Ignoring whiteboard for now
                "chat_history": []
            }

            with st.spinner("Generating question..."):
                question = room.ask_question_chain.invoke(inputs)

            st.write("**Bot's question:**", question)


if __name__ == '__main__':
    router = StreamlitRouter()
    router.register(landing_page, '/')
    router.register(room_page, '/room/<string:session_id>')
    landing_page()
