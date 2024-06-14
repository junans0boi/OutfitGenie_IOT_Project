# OutfitGenieGeocodeing.py

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
        if results.get("results"):
            address = results["results"][0].get("formatted_address")
            return address
    else:
        print(f"Error: {response.status_code}")  # HTTP 응답 상태 코드 출력
    return None
