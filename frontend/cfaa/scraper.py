import logging
from googlesearch import search
from newspaper import Article
from newspaper.article import ArticleException
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Query, Article as ArticleModel

# Set up logging
logger = logging.getLogger(__name__)


def scrape_and_store_news(query_text, search_query, start_date=datetime.today(), end_date=datetime.today()- timedelta(days=7)):
    """
    This function retrieves news articles between the given start_date and end_date for the query
    and stores them in the Django database using Django's ORM.

    Args:
        query_text (str): The query text entered by the user.
        search_query (str): The refined search query to be used in Google search.
        start_date (datetime): The start date for collecting articles.
        end_date (datetime): The end date for collecting articles.

    Returns:
        str: Success message or an error message.
    """
    # Define the number of Google results to retrieve
    num_results = 10

    try:
        # Create and save the query in the database
        query, created = Query.objects.get_or_create(
            text=query_text,
            search_query=query_text,
            defaults={'article_summary': 'null'}
        )

        # Convert dates to the format 'YYYY-MM-DD'
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # Construct the search query to include articles from the specified date range
        query_date_range = f'{query_text} after:{start_date_str} before:{end_date_str}'

        # Retrieve and store articles
        for url in search(query_date_range, num_results=num_results):
            try:
                article = Article(url)
                article.download()
                article.parse()

                if not article.publish_date:
                    article.publish_date = end_date  # Use the end_date if no publish date is available

                # Skip articles without key fields
                if not article.title or not article.text:
                    continue
                elif article.title == 'Subscribe to read':
                    continue

                # Store the article in the database
                ArticleModel.objects.create(
                    query=query,
                    publish_date=article.publish_date.date(),
                    title=article.title,
                    text=article.text,
                    url=url,
                    summary=''  # Placeholder for future summaries
                )

            except ArticleException as e:
                print(f"Failed to download article from {url}: {str(e)}")
                continue

        return "News articles successfully scraped and stored."

    except Exception as e:
        return f"An error occurred while storing articles: {str(e)}"
