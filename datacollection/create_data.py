import sqlite3

db_path = '../frontend/db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# add query to db
# cursor.execute('''
#                     INSERT INTO cfaa_topic (title)
#                     VALUES (?)
#                 ''', ("Carbon Emission India",))  # The value is passed as a tuple

cursor.execute('''
                    INSERT INTO cfaa_report (creation_day, text, basis, update, query_id,topic_id)
                    VALUES (?)
                ''', ("Carbon Emission India",))  # The value is passed as a tuple

conn.commit()
conn.close()