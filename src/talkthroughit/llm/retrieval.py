from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
import streamlit as st
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings


GEMINI_API_KEY = st.secrets['gemini']['api_key']
GEMINI_EMBEDDINGS_MODEL = st.secrets['gemini']['embeddings_model']


@st.cache_resource
def get_embeddings():
    """
    Gets the embeddings model instance.
    """
    return GoogleGenerativeAIEmbeddings(model=GEMINI_EMBEDDINGS_MODEL,
                                        google_api_key=GEMINI_API_KEY)


def create_vector_store(documents_path: Path):
    """
    Creates a vector store from documents in the given path.
    The resource is not cached here since it's part of a cached Session.
    """
    # Load all PDF documents from the specified directory
    loader = PyPDFDirectoryLoader(str(documents_path), recursive=True)
    documents = loader.load()

    # Split the loaded documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)

    # Create the vector store using the embeddings model
    vector_store = InMemoryVectorStore.from_documents(
        splits,
        embedding=get_embeddings())

    return vector_store
