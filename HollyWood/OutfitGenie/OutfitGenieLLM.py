import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

def set_api_key():
    
    # Google API 키를 환경 변수로 설정하는 함수
    os.environ["GOOGLE_API_KEY"] = "AIzaSyBZfOhQ0aVyQllnUIGB4KbTlUZZRVE8mVQ"

#더미 데이터를 반환하는 함수 - 날씨 관련 데이터를 미리 정의하여 반환
def get_dummy_data():
    
    return {
        "temperature": 20,
        "fine_dust": "나쁨",
        "rain": True,
        "snow": False
    }

# 날씨 데이터를 바탕으로 프롬프트를 생성하는 함수
# Args: data (dict): 날씨 관련 데이터가 담긴 딕셔너리
def generate_prompt(data):
    temperature = data["temperature"]
    fine_dust = data["fine_dust"]
    rain = data["rain"]
    snow = data["snow"]

    # 온도에 따른 체감 온도 문구 생성
    if temperature > 25:
        temp_feel = "따뜻할 것으로 보입니다"
    elif temperature > 15:
        temp_feel = "시원할 것으로 보입니다"
    elif temperature > 5:
        temp_feel = "쌀쌀할 것으로 보입니다"
    else:
        temp_feel = "매우 추울 것으로 보입니다"

    weather_statement = ""

    # 비와 눈에 따른 날씨 문구 생성
    if rain and snow:
        weather_statement = "오늘은 비와 눈이 올 예정입니다. 우산과 따뜻한 옷을 챙기세요."
    elif rain:
        weather_statement = "오늘은 비가 올 예정입니다. 우산을 챙기세요."
    elif snow:
        weather_statement = "오늘은 눈이 내릴 예정입니다. 따뜻하게 입으세요."
    else:
        weather_statement = "오늘은 비나 눈이 내리지 않을 예정입니다."

    # 미세먼지 상태에 따른 문구 생성
    fine_dust_statement = "공기 상태가 좋지 않으니 마스크를 착용하세요." if fine_dust == "나쁨" else "공기 상태는 좋습니다."

    # 최종 프롬프트 생성
    prompt = (
        f"오늘 날씨는 온도가 {temperature}도로 {temp_feel}. "
        f"하지만 미세먼지 상태가 {fine_dust}므로 {fine_dust_statement} "
        f"{weather_statement} 좋은 하루 되세요!"
    )
    return prompt

# 생성된 프롬프트를 바탕으로 LLM 답변을 가져오는 함수
# Args: prompt (str): 생성된 프롬프트 문자열
def get_llm_answer(prompt: str) -> str:
    
    model = ChatGoogleGenerativeAI(model="gemini-pro")  # LLM 모델 초기화
    output_parser = StrOutputParser()  # 출력 파서 초기화
    chain = model | output_parser  # 모델과 파서를 체인으로 연결
    return chain.invoke(prompt)  # 프롬프트를 전달하여 응답을 받아 반환

if __name__ == "__main__":
    set_api_key()  # Google API 키 설정
    data = get_dummy_data()  # 더미 데이터 가져오기
    prompt = generate_prompt(data)  # 프롬프트 생성
    answer = get_llm_answer(prompt)  # LLM 답변 가져오기
    print(answer)  # 답변 출력
