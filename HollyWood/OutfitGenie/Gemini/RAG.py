from operator import itemgetter
from typing import List
import base64

from langchain_core.runnables import Runnable, RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.retrievers import EnsembleRetriever
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain.pydantic_v1 import BaseModel
from langchain_core.output_parsers import StrOutputParser

from templates import SYSTEM_TEMPLATE, HUMAN_TEMPLATE, PDF_LIST

def create_gemini_pro_vision() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-pro-vision",
        convert_system_message_to_human=True
    )

def create_chat_prompt_template(system_template: str, human_template: str, images: List[str]) -> ChatPromptTemplate:
    human_messages = [{"type": "text", "text": human_template}]
    for image in images:
        human_messages.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image}"
                }
            }
        )
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            HumanMessagePromptTemplate.from_template(human_messages)
        ]
    )

def create_pdf_vector_store_ensemble_retriever(pdfs: list[str]) -> EnsembleRetriever:
    return EnsembleRetriever(
        retrievers=[
            FAISS.from_documents(
                PyPDFLoader(pdf).load_and_split(),
                GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            ).as_retriever() for pdf in pdfs
        ]
    )

def parse_page_content(documents: list[Document]) -> str:
    return "".join(document.page_content for document in documents)

def get_outfit_genie_chain(images: List[str]) -> Runnable:
    class Input(BaseModel):
        weather: str

    class Output(BaseModel):
        answer: str
        
    return (
        {
            "weather": itemgetter("weather"),
            # "context": itemgetter("question")
            # | create_pdf_vector_store_ensemble_retriever(PDF_LIST)
            # | RunnableLambda(parse_page_content)
        }
        | create_chat_prompt_template(
            SYSTEM_TEMPLATE,
            HUMAN_TEMPLATE,
            images
        )
        | create_gemini_pro_vision()
        | StrOutputParser()
    ).with_types(
        input_type=Input,
        output_type=Output
    )

def excute_outfit_genie_chain(prompt: str, images: List[str]):
    outfit_genie = get_outfit_genie_chain(images)
    return outfit_genie.invoke({"weather": prompt})