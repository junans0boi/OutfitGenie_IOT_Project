import requests
from datetime import datetime

SERVICE_KEY = "Xnp%2BTViCCwNnf67xecZvXEnev8RZ3KVpPS3uPbB44Uk14TkI%2FYNkS0vOSbypnx2c%2BOhLX2zSXHI4sdCGyck0Mw%3D%3D"
BASE_TIMES = ['0200', '0500', '0800', '1100', '1400', '1700', '2000', '2300']

# 날씨 코드 매핑 (강수 상태와 하늘 상태)
PTY_CODE = {0: '강수 없음', 1: '비', 2: '비/눈', 3: '눈', 5: '빗방울', 6: '진눈깨비', 7: '눈날림'}
SKY_CODE = {1: '맑음', 3: '구름많음', 4: '흐림'}

def get_weather(NX, NY, location):
    base_date = datetime.today().strftime("%Y%m%d")
    
    for base_time in BASE_TIMES:
        url = (
            f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
            f"?serviceKey={SERVICE_KEY}&pageNo=1&numOfRows=1000&dataType=JSON"
            f"&base_date={base_date}&base_time={base_time}&nx={NX}&ny={NY}"
        )
        
        try:
            response = requests.get(url, verify=False)
            response.raise_for_status()  # 요청이 성공적으로 처리되지 않으면 예외 발생
            data = response.json()
            
            if data['response']['header']['resultCode'] == '00':
                weather_dict = parse_weather_data(data)
                
                weather_dict['date'] = f"{base_date[:4]}년 {base_date[4:6]}월 {base_date[6:]}일"
                weather_dict['location'] = location
                
                return weather_dict
            else:
                print(f"Base Time {base_time}에 데이터가 없습니다.")
        
        except requests.exceptions.RequestException as e:
            return {"error": f"API 요청 실패: {e}"}
        except ValueError as e:
            return {"error": f"응답 JSON 파싱 실패: {e}"}

    return {"error": "모든 시간대에 대해 데이터를 가져오지 못했습니다."}

def parse_weather_data(data):
    weather_data = {}
    try:
        for item in data['response']['body']['items']['item']:
            category = item['category']
            forecast_time = item['fcstTime']
            forecast_value = item['fcstValue']
            
            if forecast_time not in weather_data:
                weather_data[forecast_time] = {}
            
            weather_data[forecast_time][category] = forecast_value

        sorted_times = sorted(weather_data.keys()) # 시간 순서대로 정렬
        parsed_data = {}
        for forecast_time in sorted_times:
            values = weather_data[forecast_time]
            update_time = f"{forecast_time[:2]}:{forecast_time[2:]}" # 시간 포맷 변경
            tmp = values.get('TMP', 'N/A')  # 기온
            wsd = values.get('WSD', 'N/A')  # 풍속
            sky = SKY_CODE.get(int(values.get('SKY', 0)), 'N/A')    # 하늘 상태
            pty = PTY_CODE.get(int(values.get('PTY', 0)), 'N/A')    # 강수 상태
            reh = values.get('REH', 'N/A')  # 습도

            # 시간대별 데이터를 변수에 저장
            parsed_data[f"hour{forecast_time[:2]}"] = (
                f"{sky}, {pty}, 기온: {tmp}°C, 습도: {reh}%, 바람: {wsd}m/s"
            )

        return parsed_data
    except KeyError as e:
        return {"error": f"데이터 처리 중 오류 발생: {e}"}
