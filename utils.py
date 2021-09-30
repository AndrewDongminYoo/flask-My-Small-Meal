# -*- coding: utf-8 -*-
from pymongo import MongoClient
import requests
client = MongoClient('mongodb://test:test@3.36.132.126', 27017)
db = client.dbGoojo
col = db.restaurant


def put_restaurant(ssid):
    """
    즐겨찾기 버튼을 클릭한 점포를 데이터베이스에 저장합니다.
    :param ssid: 요기요 데이터베이스 상점 id
    :return: None
    """
    if list(col.find({"ssid": ssid}, {"_id": False})):
        return
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
        "image": result.get("background_url")
        }
    col.insert_one(doc)


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
