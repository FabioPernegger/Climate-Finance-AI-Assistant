import logging
from googlesearch import search
from newspaper import Article
from newspaper.article import ArticleException
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Query, Article as ArticleModel

# Set up logging
logger = logging.getLogger(__name__)


def scrape_and_store_news(query_text, search_query):
    """
    This function retrieves news articles from the last 7 days for the given query and stores them in the Django database using Django's ORM.

    Args:
        query_text (str): The query text entered by the user.
        search_query (str): The refined search query to be used in Google search.

    Returns:
        str: Success message or an error message.
    """
    # Define number of Google results to retrieve
    num_results = 10

    try:
        # Create and save the query in the database
        query = Query.objects.create(text=query_text, search_query=search_query, article_summary='')

        # Get today's date and 7 days ago
        today = datetime.now()
        seven_days_ago = today - timedelta(days=7)

        # Convert dates to the format 'YYYY-MM-DD'
        today_str = today.strftime('%Y-%m-%d')
        seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%d')

        # Construct the search query to include articles from the last 7 days
        query_date_range = f'{search_query} after:{seven_days_ago_str} before:{today_str}'

        # Initialize summary text to collect summaries of all articles
        all_summaries = []

        # Retrieve and store articles
        for url in search(query_date_range, num_results=num_results):
            try:
                article = Article(url)
                article.download()
                article.parse()

                if not article.publish_date:
                    article.publish_date = today  # Use today's date if no publish date is available

                # Skip articles without key fields
                if not article.title or not article.text:
                    continue

                # Optional: Summarize the article text (e.g., first 50 words as a summary)
                article_summary = ' '.join(article.text.split()[:50])
                all_summaries.append(article_summary)

                # Store the article in the database
                ArticleModel.objects.create(
                    query=query,
                    publish_date=article.publish_date.date(),
                    title=article.title,
                    text=article.text,
                    url=url,
                    summary=article_summary
                )

            except ArticleException as e:
                print(f"Failed to download article from {url}: {str(e)}")
                continue

        # After processing articles, store all summaries in the query's article_summary field
        query.article_summary = ' '.join(all_summaries)
        query.save()

        return "News articles successfully scraped and stored."

    except Exception as e:
        return f"An error occurred while storing articles: {str(e)}"
