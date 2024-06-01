import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

def set_api_key():
    os.environ["GOOGLE_API_KEY"] = "AIzaSyBZfOhQ0aVyQllnUIGB4KbTlUZZRVE8mVQ"

def get_dummy_data():
    return {
        "temperature": 20,
        "fine_dust": "나쁨",
        "rain": True,
        "snow": False
    }

def generate_prompt(data):
    temperature = data["temperature"]
    fine_dust = data["fine_dust"]
    rain = data["rain"]
    snow = data["snow"]
    
    temp_feel = "따뜻할 것으로 보입니다" if temperature > 25 else "시원할 것으로 보입니다" if temperature > 15 else "쌀쌀할 것으로 보입니다" if temperature > 5 else "매우 추울 것으로 보입니다"
    weather_statement = ""
    
    if rain and snow:
        weather_statement = "오늘은 비와 눈이 올 예정입니다. 우산과 따뜻한 옷을 챙기세요."
    elif rain:
        weather_statement = "오늘은 비가 올 예정입니다. 우산을 챙기세요."
    elif snow:
        weather_statement = "오늘은 눈이 내릴 예정입니다. 따뜻하게 입으세요."
    else:
        weather_statement = "오늘은 비나 눈이 내리지 않을 예정입니다."

    fine_dust_statement = "공기 상태가 좋지 않으니 마스크를 착용하세요." if fine_dust == "나쁨" else "공기 상태는 좋습니다."

    prompt = (
        f"오늘 날씨는 온도가 {temperature}도로 {temp_feel}. "
        f"하지만 미세먼지 상태가 {fine_dust}므로 {fine_dust_statement} "
        f"{weather_statement} 좋은 하루 되세요!"
    )
    return prompt

def get_llm_answer(prompt: str) -> str:
    model = ChatGoogleGenerativeAI(model="gemini-pro")
    output_parser = StrOutputParser()
    chain = model | output_parser
    return chain.invoke(prompt)

if __name__ == "__main__":
    set_api_key()
    data = get_dummy_data()
    prompt = generate_prompt(data)
    answer = get_llm_answer(prompt)
    print(answer)
