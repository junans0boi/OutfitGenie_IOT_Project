# 경로 : C:\WebServer\HollyWood\WeatherNotice\WeatherNoticeGTTS.py
from gtts import gTTS
import os
# 주어진 텍스트를 음성 파일로 변환하여 저장하는 함수
# Args: text (str): 변환할 텍스트, filename (str): 저장할 파일 이름
def generate_tts(text: str, filename: str):
    
    # 출력 디렉토리가 존재하는지 확인하고, 없으면 생성
    output_dir = "C:/WebServer/HollyWood/OutfitGenie"
    os.makedirs(output_dir, exist_ok=True)
    
    # 출력 파일의 전체 경로
    filepath = os.path.join(output_dir, filename)
    
    # gTTS 객체를 생성하여 텍스트를 한국어 음성으로 변환
    tts = gTTS(text=text, lang='ko')
    
    # 음성 파일을 지정된 경로에 저장
    tts.save(filepath)
