from django.shortcuts import render
from .models import NewsArticle, Report

def discovery_page(request):
    query = request.GET.get('q')
    if query:
        articles = NewsArticle.objects.filter(title__icontains=query)
    else:
        articles = NewsArticle.objects.all()
    return render(request, 'cfaa/discovery.html', {'articles': articles})

def report_page(request):
    latest_report = Report.objects.latest('published_date')
    related_articles = latest_report.related_articles.all()
    new_articles = NewsArticle.objects.exclude(id__in=related_articles.values_list('id', flat=True)).order_by(
        '-published_date')[:5]

    return render(request, 'report.html', {
        'report': latest_report,
        'related_articles': related_articles,
        'new_articles': new_articles,
    })


