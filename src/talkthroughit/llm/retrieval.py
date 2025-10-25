from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
import streamlit as st
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings


@st.cache_resource
def get_embeddings():
    """
    Gets the embeddings model instance.
    """
    api_key = st.secrets['gemini']['api_key']
    embeddings_model = st.secrets['gemini']['embeddings_model']
    return GoogleGenerativeAIEmbeddings(model=embeddings_model,
                                        google_api_key=api_key)


def create_vector_store(documents_path: Path):
    """
    Creates a vector store from documents in the given path.
    The resource is not cached here since it's part of a cached Session.
    """
    # Load all PDF documents from the specified directory
    loader = PyPDFDirectoryLoader(str(documents_path), recursive=True)
    documents = loader.load()

    # Split the loaded documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)

    # Create the vector store using the embeddings model
    vector_store = InMemoryVectorStore.from_documents(
        splits, embedding=get_embeddings())

    return vector_store
