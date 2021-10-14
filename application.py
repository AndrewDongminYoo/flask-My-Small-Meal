# -*- coding: utf-8 -*-
import pymongo
from flask import Flask, request, jsonify, render_template, json, redirect, url_for
from flask_cors import CORS
from pymongo import MongoClient  # 몽고디비
import requests  # 서버 요청 패키지
import os
import hashlib
import jwt
import datetime
from urllib.parse import urlparse, parse_qsl

application = Flask(__name__)
cors = CORS(application, resources={r"/*": {"origins": "*"}})
if application.env == 'development':
    os.popen('mongod')
# 배포 전에 원격 db로 교체!
# client = MongoClient(os.environ.get("DB_PATH"))
client = MongoClient(os.environ.get("DB_PATH"))
SECRET_KEY = os.environ.get("JWT_KEY")

db = client.dbGoojo
restaurant_col = db.restaurant
bookmarked_col = db.bookmark
users = db.users
members = db.members
users.create_index([('uuid', pymongo.ASCENDING)], unique=True)
restaurant_col.create_index([('_id', pymongo.ASCENDING)], unique=True)
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
    # return "<h1>This is API server</h1>"
    return render_template('index.html')


@application.route('/login')
def login():
    return render_template('login.html')


@application.route('/register')
def register():
    return render_template('register.html')


@application.route('/kakao_login')
def kakao_login():
    return render_template('kakao_login.html')


@application.route('/api/login', methods=['POST'])
def api_login():
    email = request.form['email']
    pw = request.form['pw']
    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    # id, 암호화된 pw 을 가지고 해당 유저를 찾습니다.
    result = members.find_one({'email': email, 'pw': pw_hash})
    nick = result['nick']
    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload 와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp 를 담았습니다. 즉, JWT 토큰을 풀면 유저 ID 값을 알 수 있습니다.
        # exp 에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'email': email,
            'nick': nick,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        # token 을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@application.route('/api/register', methods=['POST'])
def api_register():
    email = request.form['email']
    pw = request.form['pw']
    nickname = request.form['nickname']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if members.find_one({"email": email}):
        return 403
    members.insert_one({'email': email, 'pw': pw_hash, 'nick': nickname})
    return 200


@application.route('/api/vaild', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')
    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.
    try:
        # token 을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload 를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload 와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        # find_member = members.find_one({'email': payload['email']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': payload['nick'], 'payload': payload})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'msg': '로그인 정보가 존재하지 않습니다.'})


@application.route('/redirect')
def kakao_redirect():
    # code 가져 오기
    parts = urlparse(request.full_path)
    qs = dict(parse_qsl(parts.query))
    code = qs['code']
    client_id = 'b702be3ada9cbd8f018e7545d0eb4a8d'
    # 토큰요청
    url = f'https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}' \
          f'&redirect_uri=http://localhost:5000/kakaoCallback&code={code}'
    header_1st = {'Content-Type': 'application/x-www-form-urlencoded;charset=urf-8'}
    req = requests.post(url, headers=header_1st).json()
    access_token = req['access_token']
    # 사용자 정보
    url = 'https://kapi.kakao.com/v2/user/me'
    header_2nd = {'Authorization': f'Bearer {access_token}',
                  'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
    req = requests.post(url, headers=header_2nd).json()
    try:
        user_id = req['id']
        nickname = req['properties']['nickname']
        email = req['kakao_account']['email']
        # db에 저장
        members.update({'providerId': user_id},
                       {"$set": {'email': email, 'nick': nickname, 'provider': 'kakao'}}, True)
    except Exception as e:
        print(e)
        user_id = req['id']
        nickname = req['properties']['nickname']
        # db에 저장
        members.update({'providerId': user_id},
                       {"$set": {'nick': nickname, 'provider': 'kakao'}}, True)
    # jwt 토큰 발급
    payload = {
        'id': user_id,
        'nick': nickname,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
    # kakaoLogin 리다이렉트
    return redirect(url_for("kakao_login", token=token))


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
    print(request.json)
    uuid = request.json.get('uuid')
    _id = request.json.get('_id')
    action = request.json.get('action')
    min_order = request.json.get('min_order')
    user = users.find_one({"uuid": uuid})
    print(user)
    put_restaurant(_id, min_order)
    if action == 'like':
        if not user:
            good_list = [_id]
            users.insert_one({"uuid": uuid, "like_list": good_list})
        elif _id in user['like_list']:
            pass
        else:
            good_list = user['like_list']
            good_list.append(_id)
            users.update_one({"uuid": uuid}, {"$set": {"like_list": good_list}}, upsert=True)
    elif user and _id in user['like_list']:
        good_list = user['like_list']
        good_list.remove(_id)
        users.update_one({"uuid": uuid}, {"$set": {"like_list": good_list}}, upsert=True)
    return jsonify(user)


@application.route('/api/like', methods=['GET'])
def show_bookmark():
    """
    사용자의 uuid 를 조회해 좋아요한 상품들의 리스트를 불러온다.
    * 추가할 내용 restaurants DB 에서 해당 상품들 조회해 오기\n
    :return: Response(json)
    """
    uuid = request.args.get('uuid')
    user = list(users.find({"uuid": uuid}))
    good_list = []
    if user:
        good_list = user[0]['like_list']
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
        if not int(shop["phone"]):
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
    restaurant = list(bookmarked_col.find({"_id": _id}))[0]
    return jsonify(restaurant)


@application.route('/api/address', methods=["POST"])
def search_add():
    data = request.get_data()
    query = json.loads(data, encoding='utf-8')['query']
    # query = request.json.get('query')
    return jsonify(search_address(query))


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
    bookmarked_col.insert_one(doc)


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
    application.run(port=8000)
