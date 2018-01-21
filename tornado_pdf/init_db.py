import sqlite3
conn = sqlite3.connect('../main.db')
conn.execute('''CREATE TABLE users
             (login text, password text)''')
conn.execute('''CREATE TABLE files
             (user text, name text)''')

conn.execute(''' insert into users (login, password) values ('polosate', 'polosate')''')
conn.commit()
