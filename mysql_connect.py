import mysql.connector

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "12345678"
)

my_cursor = mydb.cursor()
# create db
# my_cursor.execute("CREATE DATABASE our_users2")

# 顯示資料庫
my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)