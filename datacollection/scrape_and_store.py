import pandas as pd

from googlesearch import search

from newspaper import Article
from newspaper.article import ArticleException

import sqlite3

# Define query
query_text = 'Will the U.S. Inflation Reduction Act (IRA) remain fully intact after the 2024 presidential election?'
search_query = 'inflation reduction act after 2024 presidential election'

# Define date range
dates = pd.date_range('2024-01-01','2024-08-01' , freq='1ME')
dates_end = dates.strftime('%Y-%m-%d').tolist()
dates_begin = (dates-pd.offsets.MonthBegin(1)).strftime('%Y-%m-%d').tolist()

# Define number of google results to retrieve
num_results = 15

# connect to db
db_path = '../frontend/db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# add query to db
cursor.execute('''
                    INSERT INTO queries (text, search_query)
                    VALUES (?, ?)
                    ''', (query_text, search_query))
conn.commit()

cursor.execute("SELECT id FROM queries WHERE text = ?", (query_text,))
query_id = cursor.fetchone()[0]


# retrieve articles and store to db
for date_begin, date_end in zip(dates_begin, dates_end):

    query_date = search_query + ' after:' + date_begin + ' before:' + date_end

    for url in search(query_date, num_results=num_results):
        try:
            article = Article(url)
            article.download()
            article.parse()

            if article.publish_date == None:
                print(date_begin, 'no publish date')

            elif article.title == None:
                print(date_begin, 'no title')

            elif article.text == None:
                print(date_begin, 'no text')

            else:
                cursor.execute('''
                    INSERT INTO articles (queryid, publishdate, title, text, url)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (query_id, article.publish_date, article.title, article.text, url))
                conn.commit()

        except ArticleException as e:
            print(date_begin, 'download of article not possible')

conn.close()
