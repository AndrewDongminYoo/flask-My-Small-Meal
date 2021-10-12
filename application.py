# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template
import requests  # 서버 요청 패키지
from flask_cors import CORS
from flaskext.mysql import MySQL
import pymongo
import json  # json 응답 핸들링
import os

application = Flask(__name__)
cors = CORS(application, resources={r"/*": {"origins": "*"}})

application.config["MYSQL_DATABASE_HOST"] = "smallmeal-shop.cb0wnv8kcyrj.ap-northeast-2.rds.amazonaws.com"
application.config["MYSQL_DATABASE_PASSWORD"] = "jaryogoojo"
application.config["MYSQL_DATABASE_PORT"] = 3306
application.config["MYSQL_DATABASE_DB"] = "ebdb"
application.config["MYSQL_DATABASE_USER"] = "admin"
application.config["MYSQL_CHARSET"] = 'utf-8'

mysql = MySQL()
mysql.init_app(application)
conn = mysql.connect()
conn.autocommit(True)
cursor = conn.cursor()


# sort_list = 기본 정렬(랭킹순), 별점 순, 리뷰 수, 최소 주문 금액순, 거리 순, 배달 보증 시간순
sort_list = ["rank", "review_avg", "review_count", "min_order_value", "distance"]
order = sort_list[0]


@application.route('/')
def hello_world():  # put application's code here
    # return "<h1>This is API server</h1>"
    return render_template('index.html')


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
    uuid = request.json.get('uuid')
    ssid = request.json.get('ssid')
    action = request.json.get('action')
    min_order = request.json.get('min_order')
    user = cursor.execute(f"""select * from users where uuid = '{uuid}' from smallmeal;""")
    print(user)
    # user = list(users.find({"uuid": uuid}, {"_id": False}))
    put_restaurant(ssid, min_order)
    if action == 'like':
        if not user:
            good_list = [ssid]
            cursor.execute(f"""INSERT INTO users (uuid, like_list) VALUES ({uuid}, {good_list})""")
            # users.insert_one({"uuid": uuid, "like_list": good_list})
        elif ssid in user[0]['like_list']:
            pass
        else:
            good_list = user[0]['like_list']
            good_list.append(ssid)
            cursor.excute(f"""update users set like_list = {good_list} where uuid = {uuid};""")
            # users.update_one({"uuid": uuid}, {"$set": {"like_list": good_list}}, upsert=True)
    else:
        if user and ssid in user[0]['like_list']:
            good_list = user[0]['like_list']
            good_list.remove(ssid)
            cursor.excute(f"""update users set like_list = {good_list} where uuid = {uuid};""")
            # users.update_one({"uuid": uuid}, {"$set": {"like_list": good_list}}, upsert=True)
    return jsonify({'uuid': uuid})


@application.route('/api/like', methods=['GET'])
def show_bookmark():
    """
    사용자의 uuid 를 조회해 좋아요한 상품들의 리스트를 불러온다.
    * 추가할 내용 restaurants DB 에서 해당 상품들 조회해 오기\n
    :return: Response(json)
    """
    uuid = request.args.get('uuid')
    user = cursor.execute(f"""select uuid from users where uuid = '{uuid}';""")
    # user = list(users.find({"uuid": uuid}, {"_id": False}))
    good_list = []
    if user:
        good_list = user[0]['like_list']
    restaurants = []
    for restaurant in good_list:
        rest = cursor.excute(f"""select * from users where uuid = {uuid}""")
        # rest = list(col.find({"ssid": restaurant}, {"_id": False}))
        if len(rest) > 0:
            restaurants.extend(rest)
    return jsonify({"restaurants": restaurants})


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
    url = f'https://www.yogiyo.co.kr/api/v1/restaurants-geo/?category=1인분주문&items=30&lat={lat}&lng={long}&order={order}'
    headers = {'accept': 'application/json',
               'accept-encoding': 'gzip, deflate, br',
               'sec-ch-ua-platform': '"Windows"',
               'sec-fetch-mode': 'cors',
               'sec-fetch-site': 'same-origin',
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
        rest['categories'] = json.dumps(shop.get('categories'))
        rest['image'] = shop.get('thumbnail_url')
        rest['logo'] = shop.get('logo_url')
        rest['address'] = shop.get('address')
        rest['rating'] = shop.get('review_avg')
        rest['time'] = shop.get('open_time_description')
        rest['min_order'] = shop.get('min_order_amount')
        restaurants.append(rest)
        cursor.execute(f"""insert into 
        smallmeal (id, name, reviews, owner, categories, image, logo, address, rating, "time", min_order) 
        values ({rest['id']}, {rest['name']}, {rest['reviews']}, {rest['owner']}, {rest['categories']}, {rest['image']}, 
        {rest['logo']}, {rest['logo']}, {rest['address']}, {rest['rating']}, {rest['time']}, {rest['min_order']}) 
        from smallmeal;""")
        # DB 저장하기엔 데이터가 다소 많고, ObjectId 때문에 리턴 값을 조정해야 한다.
        # col.insert_one(rest, {"_id": False})

    return jsonify(restaurants)


@application.route('/api/detail', methods=["GET"])
def show_modal():
    ssid = request.args.get('ssid')
    restaurant = cursor.execute(f"""select * from id = {ssid} from smallmeal limit 1;""")
    # restaurant = list(col.find({"ssid": ssid}, {"_id": False}))[0]
    return jsonify(restaurant)


@application.route('/api/address', methods=["POST"])
def search_add():
    query = request.json.get('query')
    return jsonify(search_address(query))


def put_restaurant(ssid, min_order):
    """
    즐겨찾기 버튼을 클릭한 점포를 데이터베이스에 저장합니다.
    :param ssid: 요기요 데이터베이스 상점 id
    :param min_order: 최소 주문금액
    :return: None
    """
    # if list(col.find({"ssid": ssid}, {"_id": False})):
    #     return
    url = 'https://www.yogiyo.co.kr/api/v1/restaurants/'+ssid
    headers = {
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/93.0.4577.82 Safari/537.36',
        'x-apikey': 'iphoneap',
        'x-apisecret': 'fe5183cc3dea12bd0ce299cf110a75a2'}
    req = requests.post(url, headers=headers)
    result = req.json()
    doc = {
        "ssid": ssid,
        "time": result.get("open_time_description"),
        "phone": result.get("phone"),
        "name": result.get("name"),
        "categories": result.get("categories"),
        "delivery": result.get("estimated_delivery_time"),
        "address": result.get("address"),
        "image": result.get("background_url"),
        "min_order": min_order
        }
    cursor.execute(f"""insert into 
    restaurants (id, name, categories, logo, "time", min_order)
    values ({doc['ssid']}, {doc['time']}, {doc['phone']},{doc['name']}, {doc['categories']}, {doc['delivery']}, 
     {doc['address']}, {doc['image']}, {doc['min_order']}) from smallmeal;""")
    # col.insert_one(doc)


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
    url = 'https://dapi.kakao.com/v2/local/search/address.json?query='+query
    headers = {
        'Host': 'dapi.kakao.com',
        'Authorization': 'KakaoAK c67c5816d29490ab56c1fbf40bef220d'}
    req = requests.get(url, headers=headers)
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
    application.run()
