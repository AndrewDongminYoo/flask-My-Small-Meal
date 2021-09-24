from flask import Flask, request, jsonify, url_for, render_template, Response
from pymongo import MongoClient
import requests
import json
import utils
app = Flask(__name__)
client = MongoClient('localhost', 27017)  # 배포 전에 원격 db로 교체!
db = client.dbGoojo
count = 24  # 3의 배수 권장
# sort_list = 기본 정렬(랭킹순), 별점 순, 리뷰 수, 최소 주문 금액순, 거리 순, 배달 보증 시간순
sort_list = ["rank", "review_avg", "review_count", "min_order_value", "distance", "estimated_delivery_time"]
order = sort_list[0]


@app.route('/')
def hello_world():  # put application's code here
    """
    index.html 페이지를 리턴합니다.\n
    :return: str -> template('index.html')
    """
    return render_template('index.html')


@app.route('/api/like', methods=['POST'])
def like() -> Response:
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
    if action == 'like':
        if not user:
            good_list = [ssid]
            db.users.insert_one({"uuid": uuid, "like_list": good_list})
        else:
            good_list = user[0]['like_list']
            good_list.append(ssid)
            db.users.update({"uuid": uuid}, {"$set": {"like_list": good_list}}, upsert=True)
        utils.put_restaurant(ssid)
    else:
        if user:
            good_list = user[0]['like_list']
            good_list.remove(ssid)
            db.users.update({"uuid": uuid}, {"$set": {"like_list": good_list}}, upsert=True)
    return jsonify({'uuid': uuid})


@app.route('/api/like', methods=['GET'])
def show_bookmark() -> Response:
    """
    사용자의 uuid 를 조회해 좋아요한 상품들의 리스트를 불러온다.
    * 추가할 내용 restaurants DB 에서 해당 상품들 조회해 오기\n
    :return: Response(json)
    """
    uuid = request.args.get('uuid')
    user = list(db.users.find({"uuid": uuid}, {"_id": False}))
    good_list = user[0]['like_list']
    return jsonify({"restaurants": good_list})


@app.route('/api/shop', methods=['GET'])
def get_restaurant() -> Response:
    """
    위치 권한 허용 시 셋팅되는 기본 메소드. 요기요 서버에 사용자의 위도와 경도를 보내 주변 배달 점포를 조회해서
    필요한 데이터만 가공해서 리스트 형태로 프론트 엔드에 넘긴다.\n
    :return: Response(json)
    """
    lat = request.args.get('lat')
    long = request.args.get('lng')
    url = f'https://www.yogiyo.co.kr/api/v1/restaurants-geo/?items={count}&lat={lat}&lng={long}&order={order}&page=0'
    headers = {'x-apikey': 'iphoneap',
               'x-apisecret': 'fe5183cc3dea12bd0ce299cf110a75a2'}
    req = requests.get(url, headers=headers)
    res = json.loads(req.text)
    shops = res.get('restaurants')
    restaurants = list()
    for shop in shops:
        if shop.get('is_available_delivery'):
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


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
