import uuid
from pathlib import Path

import streamlit as st

from talkthroughit.llm.chat import create_ask_question_chain
from talkthroughit.llm.retrieval import create_vector_store


# Define the base directory for session data
@st.cache_data
def get_sessions_dir() -> Path:
    return Path(st.secrets['paths']['session_dir'])


class Room:
    def __init__(self, id: str) -> None:
        self.id = id

        # Initialize data directory if missing
        self.path = get_sessions_dir() / id
        self.path.mkdir(parents=True, exist_ok=True)

        # Initialize session attributes
        self.topic: str | None = None
        self.documents: list[str] | None = None

    def initialize(self, topic: str,
                   documents: list[tuple[str, bytes]]) -> None:
        """
        Initializes the session with a topic string and uploaded documents.
        """
        # Set the topic and document filenames on the session object
        self.topic = topic
        self.documents = [filename for filename, _ in documents]

        # Write documents to the session directory
        docs_path = self.path / 'documents'
        docs_path.mkdir(parents=True, exist_ok=True)
        for filename, data in documents:
            with open(docs_path / filename, 'wb') as f:
                f.write(data)

        # Create a vector store from the documents
        self.vector_store = create_vector_store(docs_path)
        self.retriever = self.vector_store.as_retriever()

        # Set up a question-asking chain
        self.ask_question_chain = create_ask_question_chain(self.retriever)


@st.cache_resource(ttl='1d')
def get_room(id: str):
    """
    Retrieves (or creates, if missing) a Room object by its identifier.
    The attached room data expires after one day.
    """
    return Room(id)


def create_room(topic: str, documents: list[tuple[str, bytes]]) -> str:
    """
    Creates a new session with the given topic and documents.
    Returns the identifier for the newly created session.
    """
    # Generate a unique session ID
    session_id = uuid.uuid4().hex

    # Initialize the session
    session = get_room(session_id)
    session.initialize(topic, documents)

    return session_id
