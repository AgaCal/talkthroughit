import streamlit as st
from streamlit_router import StreamlitRouter
from talkthroughit.rooms.room import create_room, get_room
from talkthroughit.components.room import room_page

def landing_page(router) -> None:
    st.set_page_config(page_title="talkthrough.it — Create a Session", layout="wide")

    st.title("talkthrough.it")
    # st.subheader("Your collaborative learning space")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.header("What is talkthrough.it?")
        st.write(
            """
            talkthrough.it is a tool to help you learn and retain information more effectively.
            Simply provide a topic and upload relevant documents (PDFs for now).
            We'll create a dedicated session room for you where you can:
            - Chat with an AI assistant about the topic.
            - Use a whiteboard to visualize your thoughts.
            - Write and execute code.
            - And much more!
            """
        )
        st.info("Get started on the right by creating a new session.")


    with col2:
        st.header("Create a New Session")
        with st.form(key="create_session_form"):
            topic = st.text_input("Enter a topic for your session", key="topic_input")
            uploaded_files = st.file_uploader(
                "Upload your documents (PDFs only)",
                accept_multiple_files=True,
                type=['pdf']
            )
            submit_button = st.form_submit_button(label="Create Session")

            if submit_button:
                if not topic:
                    st.error("Please enter a topic.")
                elif not uploaded_files:
                    st.error("Please upload at least one PDF file.")
                else:
                    # Process files and create room
                    documents: list[tuple[str, bytes]] = []
                    for f in uploaded_files:
                        try:
                            data = f.read()
                        except Exception as e:
                            st.error(f"Failed to read file {f.name}: {e}")
                            return
                        documents.append((f.name, data))

                    with st.spinner("Creating your session..."):
                        room_id = create_room(topic, documents)

                    st.session_state.room_id = room_id
                    router.redirect(*router.build("room_page",{"room_id" : st.session_state.room_id}))
    if "room_id" in st.session_state:
        router.redirect(*router.build("room_page",{"room_id" : st.session_state.room_id}))


if __name__ == '__main__':
    router = StreamlitRouter()
    router.register(landing_page, '/')
    router.register(room_page, '/room/<string:room_id>')
    router.serve()
