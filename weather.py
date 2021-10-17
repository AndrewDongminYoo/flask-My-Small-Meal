import requests
import json

Access_Key = "wzio4EjGxRc3sRoRK5Ar_uweqUVnD37x85qgqOtf_oU"  # 유동민 액세스키
Secret_key = "lk-ap7DJAfB-ZCtsJkNxWtFYayid7jBXsrbAy1fRNIY"  # 유동민 시크릿키
# 시간 당 50개/ 하루 1000개 요청 제한이 있어요 흐흑...
UNSPLASH = "https://api.unsplash.com/search/photos"  # 저작권 걱정 없는 조흔 사이트!
PAGE = 1  # 한번에 받을 이미지 수입니다 (10개까지 가능합니다.)
SIZE = ["raw", "full", "regular", "small", "thumb"][4]  # 이미지 사이즈입니다. 작을 수록 응답이 빠릅니다!

with open(file="./static/data/weather.json", mode="r", encoding="utf-8", newline="") as weather1:
    weather_dict = json.load(weather1)  # 55개의 날씨가 있습니다.
    for code, data in weather_dict.items():
        query = data['Description'].replace(" ", "%20")
        url = f'{UNSPLASH}?client_id={Access_Key}&query={query}%20weather&per_page={str(PAGE)}'
        req = requests.get(url)
        try:
            result = req.json()['results'][0]
            data['Images'] = result['urls']
        except TypeError:
            print("wrong type error")
        except KeyError:
            print("key not exists error")
with open(file="./static/data/weather.json", mode="w", encoding="utf-8", newline="") as weather2:
    json.dump(weather_dict, weather2, indent=4, ensure_ascii=False, allow_nan=False)
