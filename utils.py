from pymongo import MongoClient
import requests
client = MongoClient('localhost', 27017)
db = client.dbGoojo
col = db.restaurant


def put_restaurant(ssid):
    if list(col.find({"ssid": ssid}, {"_id": False})):
        url = f'https://www.yogiyo.co.kr/api/v1/restaurants/{ssid}/info/'
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
            "time": result.get("opening_time_description"),
            "phone": result.get("phone"),
            "name": result.get("crmdata").get("company_name"),
            "introduce": result.get("introduction_by_owner").get("introduction_text")
        }
        col.insert_one(doc)
