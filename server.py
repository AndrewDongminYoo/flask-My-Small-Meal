# -*- coding: utf-8 -*-
import os

s = ["""sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 10
sudo apt-get update
sudo apt-get install -y python3-pip
sudo update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1
wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.2.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo service mongod start
mongo
use admin
""", "db.createUser({user: '%s', pwd: '%s', roles:['root']});" % (os.environ.get('DB_ID'), os.environ.get('DB_PW')),
     """exit
sudo service mongod restart"""]


script = "".join(s)
