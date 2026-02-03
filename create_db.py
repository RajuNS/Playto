import MySQLdb

# Connect without selecting a database
db = MySQLdb.connect(
    host="127.0.0.1",
    user="root",
    passwd="raju143"
)

cursor = db.cursor()
try:
    cursor.execute("CREATE DATABASE IF NOT EXISTS playto_db")
    print("Database 'playto_db' created or already exists.")
except Exception as e:
    print(f"Failed to create database: {e}")
finally:
    cursor.close()
    db.close()
