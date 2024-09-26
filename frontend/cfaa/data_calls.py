from .models import Article, Query


def fetch_articles(year=None, month=None, query_id=None, limit=10):
    """
    Fetches articles based on year, month, and query_id using Django ORM.
    Optionally limits the number of articles retrieved.
    """
    articles = Article.objects.all()  # Start with all articles

    # Filter by year if provided
    if year:
        articles = articles.filter(publish_date__year=year)

    # Filter by month if provided
    if month:
        articles = articles.filter(publish_date__month=month)

    # Filter by query_id if provided
    if query_id:
        articles = articles.filter(query_id=query_id)

    # Limit the number of articles retrieved
    articles = articles[:5]

    # Return a list of dictionaries containing article id, title, and text
    return articles.values('id', 'title', 'text')



def fetch_query(query_id):
    """
    Fetches the query text based on the query_id using Django ORM.
    """
    try:
        query = Query.objects.get(id=query_id)  # Get the query by ID
        return query.text
    except Query.DoesNotExist:
        return None  # Handle the case where the query does not exist
