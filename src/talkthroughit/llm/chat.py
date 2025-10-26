import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_google_genai import ChatGoogleGenerativeAI


@st.cache_resource
def get_chat_model():
    """
    Gets the embeddings model instance.
    """
    api_key = st.secrets['gemini']['api_key']
    chat_model = st.secrets['gemini']['chat_model']
    return ChatGoogleGenerativeAI(model=chat_model, api_key=api_key)


def create_ask_question_chain(retriever: VectorStoreRetriever,
                              text_arguments: list[str] = [],
                              image_arguments: list[str] = []):
    """
    Creates a retrieval chain using the chat model and given retriever.
    The chain accepts an input dict containing keys: topic, input,
    whiteboard_image, chat_history.
    """
    # Define the prompt template for summarizing the user explanation
    summarize_prompt = ChatPromptTemplate.from_messages([
        ('system',
         "You are a layperson trying to understand a complex topic. "
         "You are given the topic and a history of the user's explanation, "
         "as well as a current visualization (whiteboard or code) and any "
         "questions you've asked so far.\n"
         "Given this, summarize the explanation so far with all relevant "
         "details from the user's prior answers, so we can use it to "
         "search for relevant information from the ground truth to "
         "compare against and make sure the user's explanation is accurate.\n"
         "The topic is:\n"
         "<topic>\n"
         "{topic}\n"
         "</topic>\n"
         + ("Additional explanation by the user:\n" if text_arguments else "")
         + "\n".join([f"<{text_arg}>\n{{text_arg}}\n</{text_arg}>"
                      for text_arg in text_arguments])),
        MessagesPlaceholder(variable_name='chat_history'),
        ('human', [
            {
                'type': 'text',
                'text': "{input}"
            },
            *[{
                'type': 'image_url',
                'image_url': "data:image/png;base64,{"
                             f"{arg}"
                             "}"
            } for arg in image_arguments]
        ]),
    ])

    # Set up a summarizing retriever chain
    chat_model = get_chat_model()
    summarizing_retriever = (
        summarize_prompt
        | chat_model
        | StrOutputParser()
        | retriever
        | (lambda docs:
           "\n\n".join(doc.page_content for doc in docs)))

    # Define the prompt template for generating a question to ask
    ask_question_prompt = ChatPromptTemplate.from_messages([
        ('system',
         "You are a layperson trying to understand a complex topic. "
         "You are given the topic and a history of the user's explanation, "
         "as well as a current visualization (whiteboard or code) and any "
         "questions you've asked so far.\n"
         "Given this, and context representing the ground truth about the "
         "topic, compare them and make sure the user's explanation is "
         "accurate.\n"
         "You should generate a thoughtful question to ask, or a potential "
         "mistake or way you could misinterpret the user's explanation, so "
         "they can clarify, expand or correct their explanation. Your goal is "
         "to help make sure the user deeply understands the topic.\n"
         "The topic is:\n"
         "<topic>\n"
         "{topic}\n"
         "</topic>\n"
         "The relevant context from the ground truth is:\n"
         "<context>\n"
         "{context}\n"
         "</context>\n"
         + ("Additional explanation by the user:\n" if text_arguments else "")
         + "\n".join([f"<{text_arg}>\n{{text_arg}}\n</{text_arg}>"
                      for text_arg in text_arguments])),
        MessagesPlaceholder(variable_name='chat_history'),
        ('human', [
            {
                'type': 'text',
                'text': "{input}"
            },
            *[{
                'type': 'image_url',
                'image_url': "data:image/png;base64,{"
                             f"{arg}"
                             "}"
            } for arg in image_arguments]
        ]),
    ])

    # Create the top-level chain
    chain = (
        RunnablePassthrough.assign(context=summarizing_retriever)
        | ask_question_prompt
        | chat_model
        | StrOutputParser())

    return chain
