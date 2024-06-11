import requests

def get_location_from_coordinates(lat, lng, api_key):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "latlng": f"{lat},{lng}",
        "key": api_key,
        "language": "ko"  # 응답 언어를 한국어로 설정
    }

    response = requests.get(base_url, params=params)
    print(response.url)  # 요청 URL을 출력하여 확인
    if response.status_code == 200:
        results = response.json()
        # print(results)  # 전체 응답 내용을 출력하여 확인
        if results.get("results"):
            address = results["results"][0].get("formatted_address")
            return address
    else:
        print(f"Error: {response.status_code}")  # HTTP 응답 상태 코드 출력
    return None

# 테스트
API_KEY = "AIzaSyBRxXtU77QsvG8Jna0y7qrwtmitZgEHYWo"  # 여기에 Google Maps API 키를 입력하세요
latitude = 37.44914902922866  # 예시 위도
longitude = 126.65696669075801  # 예시 경도

location = get_location_from_coordinates(latitude, longitude, API_KEY)
if location:
    print(f"주소: {location}")
else:
    print("위도와 경도를 주소로 변환할 수 없습니다.")
