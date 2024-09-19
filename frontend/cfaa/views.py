from django.shortcuts import render, get_object_or_404
from .models import Article
from .models import Query
from .models import Topic
from datetime import datetime


def dashboard(request):
    # Example data; replace with real queries and article counts from your database
    topics = Topic.objects.all()

    # Prepare the monitored_topics dictionary from the queried data
    monitored_topics = []
    for topic in topics:
        monitored_topics.append({
            'title': topic.title,
            'new_articles': 10,  # Get the count of associated articles
            'status': 'No significant changes',  # You can adjust the logic to determine the status
            'url': f'/reports/{topic.id}/'  # You can adjust this to link to a detailed report page
        })

    return render(request, 'cfaa/dashboard.html', {'monitored_topics': monitored_topics})

def discovery_page(request): #, queryid=1):
    # Get the Query object or return 404 if not found
    query = get_object_or_404(Query, id=1)

    # Get the current year
    current_year = datetime.now().year

    # Prepare a dictionary to hold articles for each month
    articles_by_month = {}

    # Loop through each month
    for month in range(1, 13):
        # Filter articles for the specific query and month
        articles = Article.objects.filter(query=query, publish_date__year=current_year, publish_date__month=month)[
                   :6]
        articles_by_month[month] = articles

    return render(request, 'cfaa/discovery.html', {
        'query': query,
        'articles_by_month': articles_by_month,
    })

def report_page(request):
    # latest_report = Report.objects.latest('published_date')
    # related_articles = latest_report.related_articles.all()
    #new_articles = Article.objects.exclude(id__in=related_articles.values_list('id', flat=True)).order_by(
       # '-published_date')[:5]

    return render(request, 'cfaa/report.html', {
        'report': '',#latest_report,
        'related_articles': '', #related_articles,
        'new_articles': '', # new_articles,
    })


