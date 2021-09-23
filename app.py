from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client.dbGoojo
count = 50
order = "rank"


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/shop', methods=['GET'])
def get_restaurant():
    lat = request.args.get('lat')
    long = request.args.get('long')
    url = f'https://www.yogiyo.co.kr/api/v1/restaurants-geo/?items={count}&lat={lat}&lng={long}&order={order}&page=0'
    headers = {'x-apikey': 'iphoneap',
               'x-apisecret': 'fe5183cc3dea12bd0ce299cf110a75a2'}
    req = requests.get(url, headers=headers)
    json = req.json()
    shops = json.get('restaurant')
    restaurants = list()
    for shop in shops:
        if shop.get('is_available_delivery'):
            rest = dict()
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
    return restaurants


if __name__ == '__main__':
    app.run()
