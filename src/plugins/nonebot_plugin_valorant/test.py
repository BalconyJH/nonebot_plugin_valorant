import sqlite3
conn = sqlite3.connect('valorant.db')

cursor = conn.cursor()
cursor.execute('create table if not exists user (id varchar(20) primary key, name varchar(20))')
cursor.execute('insert into user (id, name) values (\'1\', \'Michael\')')

conn.commit()
conn.close()