import requests
from datetime import datetime

SERVICE_KEY = "Xnp%2BTViCCwNnf67xecZvXEnev8RZ3KVpPS3uPbB44Uk14TkI%2FYNkS0vOSbypnx2c%2BOhLX2zSXHI4sdCGyck0Mw%3D%3D"
BASE_TIME = '0500'  # 매일 05:00시에 업데이트
NX = '55'
NY = '124'

# 날씨 코드 매핑 (강수 상태와 하늘 상태)
PTY_CODE = {0: '강수 없음', 1: '비', 2: '비/눈', 3: '눈', 5: '빗방울', 6: '진눈깨비', 7: '눈날림'}
SKY_CODE = {1: '맑음', 3: '구름많음', 4: '흐림'}

def get_weather(nx, ny):
    base_date = datetime.today().strftime("%Y%m%d")
    
    url = (
        f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
        f"?serviceKey={SERVICE_KEY}&pageNo=1&numOfRows=1000&dataType=JSON"
        f"&base_date={base_date}&base_time={BASE_TIME}&nx={NX}&ny={NY}"
    )
    
    # API 요청 URL 구성
    response = requests.get(url, verify=False)
    data = response.json()
    
    weather_string = get_weather_string(data)
    
    template = (
        f"{base_date[:4]}년 {base_date[4:6]}월 {base_date[6:]}일 {(int(NX), int(NY))}지역의 날씨는\n"
        f"{weather_string}"
    )
    
    return {"weather": template}

def get_weather_string(data):
    weather_data = {}
    for item in data['response']['body']['items']['item']:
        category = item['category']
        forecast_time = item['fcstTime']
        forecast_value = item['fcstValue']
        
        if forecast_time not in weather_data:
            weather_data[forecast_time] = {}
        
        weather_data[forecast_time][category] = forecast_value

    sorted_times = sorted(weather_data.keys()) # 시간 순서대로 정렬
    formatted_data = []
    for forecast_time in sorted_times:
        values = weather_data[forecast_time]
        update_time = f"{forecast_time[:2]}:{forecast_time[2:]}" # 시간 포맷 변경
        tmp = values.get('TMP', 'N/A')  # 기온
        wsd = values.get('WSD', 'N/A')  # 풍속
        sky = SKY_CODE.get(int(values.get('SKY', 0)), 'N/A')    # 하늘 상태
        pty = PTY_CODE.get(int(values.get('PTY', 0)), 'N/A')    # 강수 상태
        reh = values.get('REH', 'N/A')  # 습도

        # 포맷팅된 문자열 리스트에 추가
        formatted_data.append(
            f"{update_time} - {sky}, {pty}, 기온: {tmp}°C, "
            f"습도: {reh}%, 바람: {wsd}m/s"
        )

    return "\n".join(formatted_data)    # 줄바꿈으로 연결된 문자열 반환
