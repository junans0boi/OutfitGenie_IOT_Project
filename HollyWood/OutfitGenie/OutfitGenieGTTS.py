#C:\WebServer\HollyWood\WeatherNotice\WeatherNoticeGTTS.py

from gtts import gTTS
import os

def generate_tts(text: str, filename: str):
    # Ensure the output directory exists
    output_dir = "C:/WebServer/HollyWood/OutfitGenie"
    os.makedirs(output_dir, exist_ok=True)
    
    # Full path for the output file
    filepath = os.path.join(output_dir, filename)
    
    tts = gTTS(text=text, lang='ko')
    tts.save(filepath)
