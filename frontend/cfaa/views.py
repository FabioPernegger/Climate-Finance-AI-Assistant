from django.shortcuts import render, get_object_or_404, redirect

from .models import Article, Report, ReportArticle
from .models import Query
from .models import Topic
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods





from django.shortcuts import render
from .models import Topic

def dashboard(request):
    # Fetch all topics
    topics = Topic.objects.all()

    # Check if there are any topics
    monitored_topics = []
    if topics.exists():
        for topic in topics:
            # Get the latest report for the current topic
            latest_report = topic.reports.order_by('-creation_day').first()  # Fetch latest report based on creation day

            # Construct the URL for the latest report manually, using its ID
            report_url = f'/report/{latest_report.id}/' if latest_report else '#'

            # Add the topic information, including the URL for the latest report and topic id
            monitored_topics.append({
                'id': topic.id,  # Add the topic ID
                'title': topic.title,
                'new_articles': topic.articles.count(),  # Get the count of associated articles
                'status': 'No significant changes',  # Adjust the logic to determine the status
                'url': report_url  # Link to the latest report if available
            })

    # Pass information about topics to the template
    return render(request, 'cfaa/dashboard.html', {
        'monitored_topics': monitored_topics,
        'has_topics': topics.exists(),  # Boolean to check if there are topics
    })

def delete_topic(request, topic_id):
    # Get the topic by ID
    topic = get_object_or_404(Topic, id=topic_id)

    # Delete the topic
    topic.delete()
    #Topic.objects.all().delete()

    # Return a success response
    return JsonResponse({'message': 'Topic deleted successfully'}, status=200)

def discovery_page(request): #, queryid=1):
    # Get the Query object or return 404 if not found
    query = get_object_or_404(Query, id=1)
    query_id = query.id

    is_monitored = Report.objects.filter(query_id=query_id).exists()

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
        'query_id': query_id,
        'is_monitored': is_monitored,
        'articles_by_month': articles_by_month,
    })


def report_page(request, report_id):
    # Fetch the current report using the report_id
    report = get_object_or_404(Report, id=report_id)

    # Fetch the query related to this report
    query = get_object_or_404(Query, id=report.query_id)

    # Fetch all reports associated with the same query_id for the timeline
    query_reports = Report.objects.filter(query=query).order_by('creation_day')

    # Get all ReportArticle objects related to this report
    related_report_articles = ReportArticle.objects.filter(report=report)

    # Extract the articles related to the report
    related_articles = Article.objects.filter(report_articles__in=related_report_articles)

    # Implement pagination, display 2 articles per page
    paginator = Paginator(related_articles, 2)  # Show 2 articles per page
    page_number = request.GET.get('page', 1)  # Get the page number from the request
    page_obj = paginator.get_page(page_number)  # Get the articles for the current page

    if request.method == 'POST':
        # Get the submitted text from the TinyMCE editor
        report_text = request.POST.get('report_text')

        # Update the report.text field with the submitted content
        report.text = report_text
        report.save()  # Save the updated report

        return redirect('report', report_id=report.id)  # Redirect to the same page to see the updated report

    return render(request, 'cfaa/report.html', {
        'query': query.text,  # Pass the query text to the template
        'report': report,  # Pass the current report object
        'query_reports': query_reports,  # Pass all reports for the timeline
        'page_obj': page_obj,  # Paginated related articles
        'paginator': paginator,  # Pass the paginator for navigation
    })





@csrf_exempt  # Since this is an AJAX request, we'll disable CSRF for this view (if not using CSRF tokens)
def monitor_question(request):
    if request.method == 'POST':
        # Get the JSON data from the request body
        import json
        body = json.loads(request.body)
        query = body.get('query')  # Extract the question
        query_id = body.get('query_id')

        # Create a new Topic object (you can adjust this logic as needed)
        new_topic = Topic.objects.create(title=query)
        new_report = Report.objects.create(creation_day=date.today(),
                                           text="Lorem Ipsum",
                                           basis=-1,
                                           update="",
                                           query_id=query_id,
                                           topic_id=new_topic.id)

        # Return a success message as JSON
        return JsonResponse({'message': 'New topic created successfully!', 'topic_id': new_topic.id, 'report_id': new_report.id})

    return JsonResponse({'error': 'Invalid request method'}, status=400)


