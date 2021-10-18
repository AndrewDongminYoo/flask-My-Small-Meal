# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, json, redirect, url_for
from flask_cors import CORS
from pymongo import MongoClient  # 몽고디비
import requests  # 서버 요청 패키지
import os
import hashlib
import jwt
import datetime
import random
from bson.objectid import ObjectId
# import weather
from urllib.parse import urlparse, parse_qsl

KAKAO_REDIRECT_URI = 'https://www.mysmallmeal.shop/redirect'
application = Flask(__name__)
application.config['TEMPLATES_AUTO_RELOAD'] = True
cors = CORS(application, resources={r"/*": {"origins": "*"}})
if application.env == 'development':
    os.popen('mongod')
    KAKAO_REDIRECT_URI = 'http://localhost:5000/redirect'
# 배포 전에 원격 db로 교체!

client = MongoClient(os.environ.get("DB_PATH"), port=27017)
os.environ['JWT_KEY'] = 'JARYOGOOJO'
SECRET_KEY = os.environ.get("JWT_KEY")
client_id = 'b702be3ada9cbd8f018e7545d0eb4a8d'

db = client.dbGoojo
restaurant_col = db.restaurant
bookmarked_col = db.bookmark
users = db.users
members = db.members
print(client.address)

# sort_list = 기본 정렬(랭킹순), 별점 순, 리뷰 수, 최소 주문 금액순, 거리 순, 배달 보증 시간순
sort_list = ["rank", "review_avg", "review_count", "min_order_value", "distance"]
order = sort_list[0]
headers = {'accept': 'application/json', 'accept-encoding': 'gzip, deflate, br',
           'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
           'content-type': 'application/x-www-form-urlencoded',
           'referer': 'https://www.yogiyo.co.kr/mobile/',
           'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
           'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty',
           'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/94.0.4606.71 Safari/537.36',
           'x-apikey': 'iphoneap', 'x-apisecret': 'fe5183cc3dea12bd0ce299cf110a75a2'}


@application.route('/')
def hello_world():  # put application's code here
    return render_template("index.html")


@application.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', ID=client_id, URI=KAKAO_REDIRECT_URI, msg=msg)


@application.route('/register')
def register():
    return render_template('register.html')


@application.route('/kakao_login')
def kakao_login():
    return render_template('kakao_login.html')

@application.route('/api/food-recommend')
def api_food_recommend():  # put application's code here
    # 날씨 불러오기
    # 비옴
    # Thunderstorm 뇌우
    # Drizzle 이슬비
    # Rain 비
    # Squall 돌풍
    # Tornado 폭풍

    # 눈옴
    # Snow 눈

    # 맑음
    # Clear 맑은

    # 흐림
    # Clouds 흐림
    # Mist 안개
    # Smoke 연기
    # Haze 안개
    # Dust 먼지
    # Fog 안개
    # Sand 모래
    # Ash 먼지

    url = 'https://api.openweathermap.org/data/2.5/weather?lat=37.5559598&lon=126.1699723&appid=fa5d5576f3d1c8248d37938b4a3b216b&units=metric'
    req = requests.get(url).json()
    weather = req['weather'][0]['main']

    clear_arr = ['냉면','비빔밥','스테이크','떡볶이','순대','튀김','만두','회','카레','족발','보쌈']
    snow_arr = ['삼겹살','파스타','피자','설렁탕','순대국','삼계탕','해물탕']
    rain_arr = ['전','삼계탕','짜장면','짬뽕','탕수육','마라탕','곱창','감자탕','치킨']
    cloud_arr = ['떡','빵','아이스크림','햄버거','샌드위치','죽','커피']
    select_arr = ['치킨']
    if weather == "Clear":
        # print('맑음')
        select_arr = clear_arr;
    elif weather == "Snow":
        # print('눈')
        select_arr = snow_arr;
    elif weather == "Thunderstorm" or weather == "Drizzle" or weather == "Rain" or weather == "Squall" or weather == "Tornado":
        # print('비')
        select_arr = rain_arr
    else:
        # print('흐림')
        select_arr = cloud_arr

    random.shuffle(select_arr)
    select_food = select_arr[0]

    return jsonify({'food':select_food})


@application.route('/api/login', methods=['POST'])
def api_login():
    request.form = json.loads(request.data)
    email_receive = request.form['email']
    password = request.form['pw']
    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    hashed_pw = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # id, 암호화된 pw 을 가지고 해당 유저를 찾습니다.
    result = members.find_one({'email': email_receive, 'pw': hashed_pw}, {"_id": False})
    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result:
        # JWT 토큰에는, payload 와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp 를 담았습니다. 즉, JWT 토큰을 풀면 유저 ID 값을 알 수 있습니다.
        # exp 에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        nickname_receive = result['nick']
        payload = {
            'email': email_receive,
            'nick': nickname_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=3)
        }
        token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm='HS256')
        # token 을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@application.route('/api/register', methods=['POST'])
def api_register():
    request.form = json.loads(request.data)
    email_receive = request.form['email']
    password = request.form['pw']
    nickname = request.form['nickname']
    uuid = request.form['uuid']
    print('api_register uuid', uuid)
    hashed_pw = hashlib.sha256(password.encode('utf-8')).hexdigest()
    user_exists = bool(members.find_one({"email": email_receive}))
    if user_exists:
        return jsonify({'result': 'fail', 'msg': '같은 이메일의 유저가 존재합니다.'})
    find_member = members.find_one({"email": email_receive}, {"_id": False})
    if not find_member:
        user = {
            'provider': 'mysmallmeal',
            'email': email_receive,
            'pw': hashed_pw,
            'nick': nickname,
            'uuid': uuid,
        }
        members.update_one({"email": email_receive}, {"$set": user}, upsert=True)
        return jsonify({'result': 'success', 'user': nickname, 'msg': '가입이 완료되었습니다.'})
    return jsonify({'result': 'fail', 'msg': '가입에 실패했습니다.'})


@application.route('/api/valid', methods=['GET'])
def api_valid():
    """
    try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.
    token 을 시크릿키로 디코딩합니다.
    보실 수 있도록 payload 를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload 와 같은 것이 나옵니다.
    payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
    여기에선 그 예로 닉네임을 보내주겠습니다.
    :return:
    """
    token_receive = request.args.get('token')
    try:
        payload = jwt.decode(token_receive, key=SECRET_KEY, algorithms=['HS256'])
        print(payload)
        # find_member = members.find_one({'email': payload['email']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': payload['nick']})
    except jwt.ExpiredSignatureError:
        print("ExpiredSignatureError:: 로그인 시간이 만료되었습니다!")
        return redirect(url_for("login", msg="login timeout"))
    except jwt.exceptions.DecodeError:
        print("DecodeError:: 로그인 정보가 없습니다!")
        return redirect(url_for("login", msg="Cannot Login!"))


@application.route('/redirect')
def kakao_redirect():
    # code 가져 오기
    qs = dict(parse_qsl(request.query_string))
    code = qs.get(b'code').decode('utf-8')

    # 토큰요청
    url = 'https://kauth.kakao.com/oauth/token'
    body = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "code": code
    }
    token_header = {'Content-Type': 'application/x-www-form-urlencoded;charset=urf-8'}
    req = requests.post(url=url, headers=token_header, data=body).json()

    # 사용자 정보
    url = 'https://kapi.kakao.com/v2/user/me'
    info_header = {'Authorization': f'Bearer {req["access_token"]}',
                   'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
    user_info = requests.post(url, headers=info_header).json()
    print(user_info)
    email = user_info.get('kakao_account').get('email')
    user_id = user_info.get('id')
    prop = user_info.get('properties')
    nickname = "Guest"
    if prop:
        nickname = prop.get('nickname')
        profile = prop.get("thumbnail_image")
    user = {
        'providerId': user_id,
        'nick': nickname,
        'provider': 'kakao',
        'age': user_info.get('kakao_account').get('age_range')
    }
    # db에 저장
    members.update({'email': email},
                   {"$set": user}, upsert=True)
    # jwt 토큰 발급
    payload = {
        'id': user_id,
        'nick': nickname,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=3)
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm='HS256')
    # kakaoLogin 리다이렉트
    return redirect(url_for("kakao_login",
                            token=token, providerId=user_id, email=email, nickname=nickname))


@application.route('/api/like', methods=['POST'])
def like():
    """
    메인 로직 중 하나입니다. 웬만하면 건드리지 말기..!
    사용자의 id와 점포의 id를 POST 요청의 바디에 담아와,
    db에 해당하는 유저가 존재하는 지 확인하고, 있을 경우,
    1. 좋아요를 클릭한 경우 점포를 restaurants DB 에도 등록하고, 사용자의 점포 리스트에도 등록한다.
    2. 싫어요를 클릭한 경우 점포를 restaurants DB 에서 제외한다.\n
    :return: Response(json)
    """
    request.form = json.loads(request.data)
    uuid = request.form.get('uuid')  # uuid
    _id = request.form.get('_id')  # ssid
    action = request.form.get('action')
    min_order = request.form.get('min_order')
    user = users.find_one({"uuid": uuid})
    put_restaurant(_id, min_order)
    if action == 'like':
        if not user:
            good_list = [_id]
            users.insert_one({"_id": uuid, "uuid": uuid, "like_list": good_list})
        elif _id in user['like_list']:
            pass
        else:
            good_list = user['like_list']
            good_list.append(_id)
            users.update_one({"_id": uuid, "uuid": uuid}, {"$set": {"like_list": good_list}}, upsert=True)
    elif user and _id in user['like_list']:
        good_list = user['like_list']
        good_list.remove(_id)
        users.update_one({"_id": uuid, "uuid": uuid}, {"$set": {"like_list": good_list}}, upsert=True)
    return jsonify(user)


@application.route('/api/like', methods=['GET'])
def show_bookmark():
    """
    사용자의 uuid 를 조회해 좋아요한 상품들의 리스트를 불러온다.
    * 추가할 내용 restaurants DB 에서 해당 상품들 조회해 오기\n
    :return: Response(json)
    """
    uuid = request.args.get('uuid')
    user = users.find_one({"uuid": uuid})
    good_list = []
    if user:
        good_list = user['like_list']
    restaurants = []
    for restaurant in good_list:
        rest = list(bookmarked_col.find({"_id": restaurant}))
        if len(rest) > 0:
            restaurants.extend(rest)
    return jsonify({"user": user, "restaurants": restaurants})


@application.route('/api/shop', methods=['GET'])
def get_restaurant():
    """
    위치 권한 허용 시 셋팅되는 기본 메소드. 요기요 서버에 사용자의 위도와 경도를 보내 주변 배달 점포를 조회해서
    필요한 데이터만 가공해서 리스트 형태로 프론트 엔드에 넘긴다.\n
    :return: Response(json)
    """
    lat = request.args.get('lat')
    long = request.args.get('lng')
    global order
    order = request.args.get('order')
    if not order:
        order = "rank"
    url = f'https://www.yogiyo.co.kr/api/v1/restaurants-geo/?category=1인분주문&items=99&lat={lat}&lng={long}&order={order}'
    res = requests.get(url, headers=headers).json()
    shops = res.get('restaurants')
    restaurants = list()
    for shop in shops:
        rest = dict()
        if not bool(int(shop["phone"])):
            continue
        rest['_id'] = shop.get('id')
        rest['name'] = shop.get('name')
        rest['reviews'] = shop.get('review_count')
        rest['owner'] = shop.get('owner_reply_count')
        rest['categories'] = shop.get('categories')
        rest['image'] = shop.get('thumbnail_url')
        rest['logo'] = shop.get('logo_url')
        rest['address'] = shop.get('address')
        rest['rating'] = shop.get('review_avg')
        rest['time'] = f"{shop.get('begin')[:5]} - {shop.get('end')[:5]}"
        rest['min_order'] = shop.get('min_order_amount')
        rest['lng'] = shop.get('lng')
        rest['lat'] = shop.get('lat')
        rest['phone'] = shop.get('phone')
        restaurants.append(rest)
        restaurant_col.update_one({"_id": shop['id']}, {"$set": rest}, upsert=True)
    return jsonify(restaurants)


@application.route('/api/detail', methods=["GET"])
def show_modal():
    _id = request.args.get('_id')
    restaurant = bookmarked_col.find_one({"_id": int(_id)})
    return jsonify(restaurant)


@application.route('/api/address', methods=["POST"])
def search_add():
    data = request.get_data()
    query = json.loads(data, encoding='utf-8')['query']
    # query = request.json.get('query')
    return jsonify(search_address(query))
#
#
# @application.route('api/weather', methods=["GET"])
# def declare_weather():
#     weather_code = request.args.get('code')
#     image_format = request.args.get('size')
#     # result = weather.get_weather(code=weather_code, size=image_format)
#     return jsonify({'result': result})


def put_restaurant(_id, min_order):
    """
    즐겨찾기 버튼을 클릭한 점포를 데이터베이스에 저장합니다.
    :param _id: 요기요 데이터베이스 상점 id
    :param min_order: 최소 주문금액
    :return: None
    """
    if list(bookmarked_col.find({"_id": _id})):
        return
    url = 'https://www.yogiyo.co.kr/api/v1/restaurants/' + str(_id)
    req = requests.post(url, headers=headers)
    result = req.json()
    doc = {
        "_id": _id,
        "time": result.get("open_time_description"),
        "phone": result.get("phone"),
        "name": result.get("name"),
        "categories": result.get("categories"),
        "delivery": result.get("estimated_delivery_time"),
        "address": result.get("address"),
        "image": result.get("background_url"),
        "min_order": min_order
    }
    bookmarked_col.update_one({"_id": _id}, {"$set": doc}, upsert=True)


def search_address(query):
    """
    사용자가 검색 창에 직접 주소를 입력했을 때, 카카오맵 api 를 통해 주소를 위도경도로 변환합니다.\n
    :param query: 찾고자 하는 주소
    :return: doc(dict) {
        address: 찾고자 하는 주소 도로명 주소,
        lat: 찾고자 하는 지역의 x좌표,
        long: 찾고자 하는 지역의 y 좌표
    }
    """
    url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + query
    _header = {
        'Host': 'dapi.kakao.com',
        'Authorization': 'KakaoAK c67c5816d29490ab56c1fbf40bef220d'}
    req = requests.get(url, headers=_header)
    result = req.json()
    documents = result['documents'][0]
    address = documents['address_name']
    lat = documents['y']
    lng = documents['x']
    doc = {
        "address": address,
        "lat": lat,
        "long": lng
    }
    return doc


if __name__ == '__main__':
    application.debug = True
    application.run(port=8000, debug=True)
