#C:\WebServer\HollyWood\WeatherNotice\main.py
import os
from WeatherNoticeLLM import set_api_key, get_dummy_data, generate_prompt, get_llm_answer
from WeatherNoticeGTTS import generate_tts

def main():
    set_api_key()
    data = get_dummy_data()
    prompt = generate_prompt(data)
    answer = get_llm_answer(prompt)
    
    print("Generated LLM Answer: ", answer)
    
    # Generate TTS from LLM answer and save it as an mp3 file
    output_filename = "weather_notice.mp3"
    generate_tts(answer, output_filename)
    print(f"TTS generated and saved as {output_filename}")

if __name__ == "__main__":
    main()
