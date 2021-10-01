# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, Response
from pymongo import MongoClient  # 몽고디비
import requests  # 서버 요청 패키지
import json  # json 응답 핸들링
import utils  # 내부 파일 모듈화
app = Flask(__name__)
client = MongoClient('mongodb://jaryo:goojo@3.36.132.126:27017/dbGoojo?authSource=admin')
# client = MongoClient('localhost', 27017)  # 배포 전에 원격 db로 교체!
db = client.dbGoojo

# sort_list = 기본 정렬(랭킹순), 별점 순, 리뷰 수, 최소 주문 금액순, 거리 순, 배달 보증 시간순
sort_list = ["rank", "review_avg", "review_count", "min_order_value", "distance"]
order = sort_list[0]


@app.route('/')
def hello_world():  # put application's code here
    """
    index.html 페이지를 리턴합니다.\n
    :return: str -> template('index.html')
    """
    return render_template('index.html')


@app.route('/api/like', methods=['POST'])
def like():
    """
    메인 로직 중 하나입니다. 웬만하면 건드리지 말기..!
    사용자의 id와 점포의 id를 POST 요청의 바디에 담아와,
    db에 해당하는 유저가 존재하는 지 확인하고, 있을 경우,
    1. 좋아요를 클릭한 경우 점포를 restaurants DB 에도 등록하고, 사용자의 점포 리스트에도 등록한다.
    2. 싫어요를 클릭한 경우 점포를 restaurants DB 에서 제외한다.\n
    :return: Response(json)
    """
    uuid = request.json.get('uuid')
    ssid = request.json.get('ssid')
    action = request.json.get('action')
    user = list(db.users.find({"uuid": uuid}, {"_id": False}))
    utils.put_restaurant(ssid)
    if action == 'like':
        if not user:
            good_list = [ssid]
            db.users.insert_one({"uuid": uuid, "like_list": good_list})
        elif ssid in user[0]['like_list']:
            pass
        else:
            good_list = user[0]['like_list']
            good_list.append(ssid)
            db.users.update({"uuid": uuid}, {"$set": {"like_list": good_list}}, upsert=True)
    else:
        if user and ssid in user[0]['like_list']:
            good_list = user[0]['like_list']
            good_list.remove(ssid)
            db.users.update({"uuid": uuid}, {"$set": {"like_list": good_list}}, upsert=True)
    return jsonify({'uuid': uuid})


@app.route('/api/like', methods=['GET'])
def show_bookmark():
    """
    사용자의 uuid 를 조회해 좋아요한 상품들의 리스트를 불러온다.
    * 추가할 내용 restaurants DB 에서 해당 상품들 조회해 오기\n
    :return: Response(json)
    """
    uuid = request.args.get('uuid')
    user = list(db.users.find({"uuid": uuid}, {"_id": False}))
    good_list = []
    if user:
        good_list = user[0]['like_list']
    restaurants = []
    for restaurant in good_list:
        rest = list(db.restaurant.find({"ssid": restaurant}, {"_id": False}))
        if len(rest) > 0:
            restaurants.extend(rest)
    return jsonify({"restaurants": restaurants})


@app.route('/api/shop', methods=['GET'])
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
    cat = "1인분주문"
    count = 45  # 3의 배수 권장
    url = 'https://www.yogiyo.co.kr/api/v1/restaurants-geo/?category=' + cat + '&items=45&lat=' + lat\
          + "&lng=" + long + '&order=' + order + '&page=0'
    headers = {'accept': 'application/json', 'accept-encoding': 'gzip, deflate, br',
               'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
               'content-type': 'application/x-www-form-urlencoded',
               'if-none-match': '"9e9d0a63ef118f7f4720275c2db776a8;gzip"',
               'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
               'sec-ch-ua-platform': '"Windows"', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/93.0.4577.82 Safari/537.36',
               'x-apikey': 'iphoneap', 'x-apisecret': 'fe5183cc3dea12bd0ce299cf110a75a2'}
    req = requests.get(url, headers=headers)
    res = json.loads(req.text)
    shops = res.get('restaurants')
    restaurants = list()
    for shop in shops:
        rest = dict()
        rest['id'] = shop.get('id')
        rest['name'] = shop.get('name')
        rest['reviews'] = shop.get('review_count')
        rest['owner'] = shop.get('owner_reply_count')
        rest['categories'] = shop.get('categories')
        rest['image'] = shop.get('thumbnail_url')
        rest['logo'] = shop.get('logo_url')
        rest['address'] = shop.get('address')
        rest['rating'] = shop.get('review_avg')
        rest['time'] = shop.get('open_time_description')
        rest['min_order'] = shop.get('min_order_amount')
        restaurants.append(rest)
        # DB 저장하기엔 데이터가 다소 많고, ObjectId 때문에 리턴 값을 조정해야 한다.
        # db.restaurant.insert_one(rest, {"_id": False})
    return jsonify(restaurants)


@app.route('/api/address', methods=["POST"])
def search_add():
    query = request.json.get('query')
    return jsonify(utils.search_address(query))


if __name__ == '__main__':
    app.run('0.0.0.0')
