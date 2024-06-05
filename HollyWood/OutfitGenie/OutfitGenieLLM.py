from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
import base64

model = ChatGoogleGenerativeAI(
    model="gemini-pro-vision",
    google_api_key="AIzaSyCVYo1TfznZGAvncURyLLB7nBH9ELMPPQI"
)

def recommandClothes(prompt, images):
    global model
    # images preprocessing
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": images
            }
        ]
    )
    chain = model | StrOutputParser()
    result = chain.invoke([message])
    return result

image_url = open('image/test.jpeg', 'rb')
image = f"data:image/jpeg;base64,{base64.b64encode(image_url.read()).decode('utf-8')}"

result = recommandClothes("패션 분석 ㄱ", image)
print(result)