import MySQLdb

db = MySQLdb.connect(host="127.0.0.1", user="root", passwd="raju143", db="playto_db")
cursor = db.cursor()
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print("Tables in playto_db:")
for table in tables:
    print(table[0])
db.close()
