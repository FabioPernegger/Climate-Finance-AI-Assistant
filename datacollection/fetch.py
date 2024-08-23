import sqlite3
import pandas as pd

db_path = '../frontend/db.sqlite3'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Define the year, month, and query_id to filter by
year = '2024'
month = '07'
query_id = '1'

query = '''
SELECT id, queryid, publishdate, url, title, text
FROM articles
WHERE strftime('%Y', publishdate) = ? AND strftime('%m', publishdate) = ? AND queryid = ?
'''

cursor.execute(query, (year, month, query_id))
articles = cursor.fetchall()

# Convert to dataframe
df = pd.DataFrame(articles, columns=['id', 'queryid', 'publishdate', 'url', 'title', 'text'])

conn.close()

print(df.to_string())