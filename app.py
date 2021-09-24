from flask import Flask, request, jsonify, url_for, render_template
from pymongo import MongoClient
import requests
import json
app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client.dbGoojo
count = 24
order = "rank"


@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')


@app.route('/api/like', methods=['POST'])
def like():
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
    else:
        if user:
            good_list = user[0]['like_list']
            good_list.remove(ssid)
            db.users.update({"uuid": uuid}, {"$set": {"like_list": good_list}}, upsert=True)
    return jsonify({'uuid': uuid})


@app.route('/api/shop', methods=['GET'])
def get_restaurant():
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
            db.restaurant.insert_one(rest)
    return jsonify(restaurants)


@app.route('/api/like', methods=['GET'])
def show_bookmark():
    uuid = request.args.get('uuid')
    user = list(db.users.find({"uuid": uuid}, {"_id": False}))
    good_list = user[0]['like_list']
    return jsonify({"restaurant": good_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
