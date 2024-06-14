import sys
import os
import aiomysql
import logging
from datetime import datetime
from typing import List
from operator import itemgetter  # 추가된 임포트
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain.pydantic_v1 import BaseModel
from langchain_core.output_parsers import StrOutputParser
from gtts import gTTS

# PDF 파일 경로
PDF_PATH = os.path.join(os.path.dirname(__file__), "Outfit Coordination Guide.pdf")

def create_gemini_pro_vision() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-pro-vision",
        convert_system_message_to_human=True
    )

def create_chat_prompt_template(human_template: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([{"type": "text", "text": human_template}])

def create_pdf_vector_store_ensemble_retriever(pdf: str) -> FAISS:
    return FAISS.from_documents(
        PyPDFLoader(pdf).load_and_split(),
        GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    ).as_retriever()

def parse_page_content(documents: List[Document]) -> str:
    return "".join(document.page_content for document in documents)

def get_outfit_genie_chain() -> Runnable:
    class Input(BaseModel):
        weather: str

    class Output(BaseModel):
        answer: str
        
    return (
        {"weather": itemgetter("weather")}
        | create_chat_prompt_template(
            "{weather}"
        )
        | create_gemini_pro_vision()
        | StrOutputParser()
    ).with_types(
        input_type=Input,
        output_type=Output
    )

def execute_outfit_genie_chain(prompt: str):
    outfit_genie = get_outfit_genie_chain()
    return outfit_genie.invoke({"weather": prompt})

def generate_tts(text: str, filename: str):
    output_dir = "C:/WebServer/HollyWood/OutfitGenie"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    tts = gTTS(text=text, lang='ko')
    tts.save(filepath)
    return filepath

async def get_user_outfits(user_id: int, conn) -> List[str]:
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT Category, Color FROM outfitgenie_clothes WHERE UserID = %s", (user_id,))
        rows = await cursor.fetchall()
        return [{"category": row["Category"], "color": row["Color"]} for row in rows]

async def set_weather_for_user(user_id: int, conn):
    # 여기서는 예시로 /setweather/{user_id}에서 날씨 데이터를 가져옵니다.
    url = f"http://hollywood.kro.kr/setweather/{user_id}"
    response = requests.get(url)
    return response.json()

async def scheduled_task():
    async with aiomysql.create_pool(**DATABASE) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT UserID FROM outfitgenie_users")
                users = await cursor.fetchall()
                for user in users:
                    user_id = user["UserID"]
                    try:
                        # 날씨 데이터 업데이트
                        weather_response = await set_weather_for_user(user_id, conn)
                        weather_info = weather_response["hour" + str(datetime.now().hour).zfill(2)]
                        
                        # 사용자의 옷 데이터 가져오기
                        user_outfits = await get_user_outfits(user_id, conn)
                        
                        # LLM을 통해 코디 추천 생성
                        outfit_prompt = f"{weather_response['date']} {weather_response['location']}의 날씨는 {weather_info}입니다. 적절한 옷차림을 추천해 주세요. 사용자의 옷: {user_outfits}"
                        llm_response = execute_outfit_genie_chain(outfit_prompt)
                        
                        # TTS 생성 및 저장
                        tts_text = llm_response["answer"]
                        filename = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                        filepath = generate_tts(tts_text, filename)
                        
                        await cursor.execute(
                            "INSERT INTO outfitgenie_gtts (UserID, Filename, FilePath) VALUES (%s, %s, %s)",
                            (user_id, filename, filepath)
                        )
                        await conn.commit()
                    except Exception as e:
                        logging.error(f"Error processing user {user_id}: {str(e)}")
