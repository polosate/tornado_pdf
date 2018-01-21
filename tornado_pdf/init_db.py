import sqlite3
conn = sqlite3.connect('../main.db')
# conn.execute('''CREATE TABLE users
#              (login text, password text)''')
# conn.execute('''CREATE TABLE files
#              (user text, name text)''')
cursor = conn.cursor()
cursor.execute(''' select * from files ''')
print(cursor.fetchall())
cursor.execute(''' insert into files values ('blah', 'blahbllah') ''')
conn.commit()
cursor.execute(''' select * from files ''')
print(cursor.fetchall())
