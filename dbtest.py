import pymysql


conn = pymysql.connect(
    host='smallmeal.cb0wnv8kcyrj.ap-northeast-2.rds.amazonaws.com',
    port=3306,
    user='admin',
    password='jaryogoojo',
    db='dbGoojo',
    charset='utf8'
)

cursor = conn.cursor()

print(cursor)
print(conn)