import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel


class QuestionResponse(BaseModel):
    good_enough: bool
    question: str


class ResponseEvaluation(BaseModel):
    good_enough: bool


@st.cache_resource
def get_chat_model():
    """
    Gets the embeddings model instance.
    """
    api_key = st.secrets['gemini']['api_key']
    chat_model = st.secrets['gemini']['chat_model']
    return ChatGoogleGenerativeAI(model=chat_model, api_key=api_key)


def make_retrieval_query(inputs: dict) -> str:
    # Filter user messages and collate them for a query to the retriever
    topic = inputs['topic']
    history = inputs.get('chat_history', [])

    user_messages = [msg for role, msg in history if role == 'user']
    return (
        f"Topic: {topic}\n"
        f"Explanation so far:\n"
        f"{' '.join(user_messages)}"
        f"\nCurrent input:\n"
        f"{inputs['input']}")


def create_ask_question_chain(retriever: VectorStoreRetriever,
                              text_arguments: list[str] = [],
                              image_arguments: list[str] = []):
    """
    Creates a retrieval chain using the chat model and given retriever.
    The chain accepts an input dict containing keys: topic, input,
    whiteboard_image, chat_history.
    """
    # Set up a basic retriever chain
    chat_model = get_chat_model()
    retriever_chain = (
        RunnableLambda(make_retrieval_query)
        | retriever
        | (lambda docs:
           "\n\n".join(doc.page_content for doc in docs)))

    # Define the prompt template for generating a question to ask
    system_message = "".join([
        "You are a layperson trying to understand a complex topic. ",
        "You are given the topic and a history of the user's explanation, ",
        "as well as a current visualization (whiteboard or code) and any ",
        "questions you've asked so far.\n",
        "Given this, and context representing the ground truth about the ",
        "topic, compare them and make sure the user's explanation is ",
        "accurate.\n",
        "Based on the comparison, determine if the user's explanation is ",
        "complete and accurate enough that no further clarification is ",
        "needed. If the explanation is good enough, set good_enough to true ",
        "and provide a concise message in the question field summarizing ",
        "how you understand the topic. If clarification is needed, set ",
        "good_enough to false and provide a thoughtful question to ask in ",
        "the question field, or a potential mistake or way you could ",
        "misinterpret the user's explanation, so they can clarify, expand ",
        "or correct their explanation. DO NOT PROVIDE INFORMATION OR USE THE "
        "CONTEXT FOR THIS QUESTION. ONLY USE THE USER'S EXPLANATION. "
        "Your goal is to help make sure the user deeply understands the "
        "topic.\n",
        "While creating a question do NOT be too leading. YOU MUST ",
        "pretend you know very little about the topic.\n",
        "The topic is:\n",
        "<topic>\n",
        "{topic}\n",
        "</topic>\n",
        "The relevant context from the ground truth is:\n",
        "<context>\n",
        "{context}\n",
        "</context>\n",
        ("Additional explanation by the user:\n" if text_arguments else ""),
        "\n".join([(f"<{text_arg}>\n"
                    "{" + text_arg + "}\n"
                    f"</{text_arg}>")
                   for text_arg in text_arguments]),
        "\n\nOutput your response as a JSON object in the format: ",
        "{{\"good_enough\": boolean, \"question\": \"string\"}}"
    ])
    ask_question_prompt = ChatPromptTemplate.from_messages([
        ('system', system_message),
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
        RunnablePassthrough.assign(context=retriever_chain)
        | ask_question_prompt
        | chat_model.with_structured_output(QuestionResponse))

    return chain


def create_streamed_ask_question_chain(retriever: VectorStoreRetriever,
                                       text_arguments: list[str] = [],
                                       image_arguments: list[str] = []):
    """
    Creates a retrieval chain using the chat model and given retriever.
    The chain accepts an input dict containing keys: topic, input,
    whiteboard_image, chat_history.

    This version only streams the question output; good_enough is generated
    with a separate pass afterwards.
    """
    # Set up a basic retriever chain
    chat_model = get_chat_model()
    retriever_chain = (
        RunnableLambda(make_retrieval_query)
        | retriever
        | (lambda docs:
           "\n\n".join(doc.page_content for doc in docs)))

    # Define the prompt template for generating a question to ask
    system_message = "".join([
        "You are a layperson trying to understand a complex topic. ",
        "You are given the topic and a history of the user's explanation, ",
        "as well as a current visualization (whiteboard or code) and any ",
        "questions you've asked so far.\n",
        "Given this, and context representing the ground truth about the ",
        "topic, compare them and make sure the user's explanation is ",
        "accurate.\n",
        "Based on the comparison, determine if the user's explanation is ",
        "complete and accurate enough that no further clarification is ",
        "needed. If the explanation is good enough, provide a concise message "
        "stating that you understand the topic. If clarification is needed, "
        "provide a thoughtful question to ask, or a potential mistake or way "
        "you could misinterpret the user's explanation, so they can clarify, "
        "expand or correct their explanation. Your goal is to help make sure "
        "the user deeply understands the topic.\n",
        "The topic is:\n",
        "<topic>\n",
        "{topic}\n",
        "</topic>\n",
        "The relevant context from the ground truth is:\n",
        "<context>\n",
        "{context}\n",
        "</context>\n",
        ("Additional explanation by the user:\n" if text_arguments else ""),
        "\n".join([(f"<{text_arg}>\n"
                    "{" + text_arg + "}\n"
                    f"</{text_arg}>")
                   for text_arg in text_arguments]),
    ])
    ask_question_prompt = ChatPromptTemplate.from_messages([
        ('system', system_message),
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
        RunnablePassthrough.assign(context=retriever_chain)
        | ask_question_prompt
        | chat_model)

    return chain


@st.cache_resource
def get_or_create_evaluate_response_chain():
    """
    Creates a chain to evaluate whether the streamed response indicates
    sufficient understanding.
    """
    chat_model = get_chat_model()
    system_message = "".join([
        "You are given a response from a layperson trying to understand ",
        "a complex topic. Based on their response, determine if they have ",
        "demonstrated sufficient understanding of the topic.\n",
        "If they have demonstrated sufficient understanding, output true ",
        "for good_enough. Otherwise, output false for good_enough.\n",
        "\n\nOutput your response as a JSON object in the format: ",
        "{\"good_enough\": boolean}"
    ])
    evaluate_response_prompt = ChatPromptTemplate.from_messages([
        ('system', system_message),
        ('human', [
            {
                'type': 'text',
                'text': "{response}"
            }
        ]),
    ])

    # Create the chain
    chain = (
        evaluate_response_prompt
        | chat_model.with_structured_output(ResponseEvaluation))

    return chain


def evaluate_response(response_text: str) -> bool:
    """
    Evaluates the given response text to determine if it indicates
    sufficient understanding.
    """
    chain = get_or_create_evaluate_response_chain()
    response: ResponseEvaluation = chain.invoke(
        {'response': response_text})  # type: ignore

    return response.good_enough
