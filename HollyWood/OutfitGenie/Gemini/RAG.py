from operator import itemgetter
import base64

from langchain_core.runnables import Runnable, RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.messages import HumanMessage
from langchain.retrievers import EnsembleRetriever
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain.pydantic_v1 import BaseModel
from langchain_core.output_parsers import StrOutputParser

from templates import SYSTEM_TEMPLATE, EXAMPLES, HUMAN_TEMPLATE, PDF_LIST

def create_gemini_pro_vision() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-pro-vision",
        convert_system_message_to_human=True
    )

def create_chat_prompt_template_with_few_shot(system_template: str, examples: list[dict[str, str]], human_template: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            FewShotChatMessagePromptTemplate(
                example_prompt=ChatPromptTemplate.from_messages(
                    [
                        ("human", "질문: {question}"),
                        ("ai", "답변: {answer}\n")
                    ]
                ),
                examples=examples
            ),
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": human_template
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64.b64encode(image.read()).decode('utf-8')}"
                    } for image in images
                ]
            )
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

def get_outfit_genie_chain() -> Runnable:
    class Input(BaseModel):
        question: str
    class Output(BaseModel):
        answer: str
    return (
        {
            "question": itemgetter("question"),
            "context": itemgetter("question")
            | create_pdf_vector_store_ensemble_retriever(PDF_LIST)
            | RunnableLambda(parse_page_content)
        }
        | create_chat_prompt_template_with_few_shot(
            SYSTEM_TEMPLATE,
            EXAMPLES,
            HUMAN_TEMPLATE
        )
        | create_gemini_pro_vision()
        | StrOutputParser()
    ).with_types(
        input_type=Input,
        output_type=Output
    )

if __name__ == "__main__":
    outfit_genie = get_outfit_genie_chain()
    print(outfit_genie.invoke({"question": "Hello who are you"}))