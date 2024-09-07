import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

from llm_calls import generate_summary, generate_summary_over_articles
from data_funcs import fetch_articles, store_summary, fetch_query

load_dotenv()
openai_api_key = os.getenv("OPENAI_KEY")

client = OpenAI(api_key=openai_api_key)


# Get query text based on id
query_id = 1
query = fetch_query(query_id=query_id)


## Generate summary for each article
#data = fetch_articles(query_id = query_id)
#
#for article in data:
#    article_id = article[0]
#    title = article[1]
#    text = article[2]
#
#    summary = generate_summary(client, query, title, text)
#
#    print(article_id)
#    print(summary)
#
#    store_summary(summary, article_id)


## Generate summary for each month
#year = '2024'
#dates = pd.date_range('2024-01-01','2024-08-01' , freq='1ME')
#months = dates.strftime('%m').tolist()
#
#for month in months:
#
#    data = fetch_articles(year=year, month=month, query_id=query_id)
#
#    articles = []
#    for article in data:
#        articles.append(article[1] + ' ' + article[2])
#
#    summary = generate_summary_over_articles(client, query, articles)
#    print(summary)
#
#    store_summary(summary, date=year+'-'+month+'-01', query_id=query_id)