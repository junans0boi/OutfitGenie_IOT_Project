import os
from HollyWood.OutfitGenie.OutfitGenieLLM import set_api_key, get_dummy_data, generate_prompt, get_llm_answer
from HollyWood.OutfitGenie.OutfitGenieGTTS import generate_tts

# 메인 함수로, API 키 설정, 더미 데이터 가져오기, 프롬프트 생성,
# LLM 답변 가져오기, TTS 생성 및 저장을 수행합니다.
def main():
    set_api_key()  # Google API 키 설정
    data = get_dummy_data()  # 더미 데이터 가져오기
    prompt = generate_prompt(data)  # 프롬프트 생성
    answer = get_llm_answer(prompt)  # LLM 답변 가져오기
    
    print("Generated LLM Answer: ", answer)  # LLM 답변 출력
    
    # LLM 답변을 기반으로 TTS 생성 및 mp3 파일로 저장
    output_filename = "Outfit_Genie.mp3"  # 출력 파일 이름 설정
    generate_tts(answer, output_filename)  # TTS 생성 및 저장
    print(f"TTS generated and saved as {output_filename}")  # TTS 생성 완료 메시지 출력

if __name__ == "__main__":
    main()  # 메인 함수 실행
