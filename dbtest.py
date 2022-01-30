import atexit
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="postgres")

cursor = conn.cursor()

cursor.execute('INSERT INTO newtable VALUES (\'abc\',\'cba\')')

conn.commit()
cursor.close()
conn.close()

@atexit.register
def goodbye():
    print('You are now leaving the Python sector.')