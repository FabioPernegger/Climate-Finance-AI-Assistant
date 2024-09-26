from django.shortcuts import render, get_object_or_404, redirect

import os
import environ
from openai import OpenAI
from .models import Article, Report, ReportArticle
from .models import Query
from .models import Topic
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from .scraper import scrape_and_store_news
from .llm_calls import generate_summary_over_articles, generate_updated_report
import json





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

def discovery_page(request):
    # Define the OpenAI client inside the view
    env = environ.Env()
    environ.Env.read_env()

    # Get OpenAI API Key
    OPENAI_API_KEY = env('OPENAI_API_KEY')
    client = OpenAI(api_key=OPENAI_API_KEY)  # Instantiate the OpenAI client

    if request.method == 'GET':
        query_text = request.GET.get('query', '')  # Get the query from the search bar

        if query_text:
            # Check if the query already exists in the database
            existing_query = Query.objects.filter(text=query_text).first()

            if existing_query:
                query = existing_query
                # Fetch the articles associated with the query
                articles = Article.objects.filter(query=query)
            else:
                # If the query doesn't exist, call the scraper function
                search_query = query_text  # You can refine the query if necessary
                result = scrape_and_store_news(query_text=query_text, search_query=search_query)

                # Retrieve the newly created query
                query = get_object_or_404(Query, text=query_text)
                # Fetch the newly scraped articles
                articles = Article.objects.filter(query=query)

            # Prepare the articles as an array of strings (article text only)
            article_texts = [article.text for article in articles]

            # Check if the summary is 'null' or empty after either scenario
            if query.article_summary == 'null' or not query.article_summary:
                # Generate a summary over the articles if the summary is 'null'
                summary = generate_summary_over_articles(
                    client,
                    query.text,  # Pass query as a string (query.text)
                    article_texts,  # Pass articles as an array of strings (article texts)
                    max_tokens=200,
                    temperature=0,
                    top_p=0.5
                )

                # Update the query with the generated summary
                query.article_summary = summary
                query.save()  # Save the updated query with the new summary

            # Check if the query is being monitored (using the Report model)
            is_monitored = Report.objects.filter(query=query).exists()

        else:
            # If no query is entered, load a default query or handle this case
            query = get_object_or_404(Query, id=1)  # Replace with any default query logic
            articles = Article.objects.filter(query=query).order_by('-publish_date')[:10]
            is_monitored = Report.objects.filter(query=query).exists()

        # Prepare the context for the template
        context = {
            'query': query,
            'query_id': query.id,  # Pass the query ID
            'articles': articles,
            'is_monitored': is_monitored  # Pass the monitoring flag
        }

        return render(request, 'cfaa/discovery.html', context)


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

    # If the report is edited and saved via the form (POST request)
    if request.method == 'POST':
        # Get the submitted text from the TinyMCE editor
        report_text = request.POST.get('report_text')

        # Update the report.text field with the submitted content
        report.text = report_text
        report.save()  # Save the updated report

        # Redirect to the same page to reload the updated content
        return redirect('report', report_id=report.id)

    # Render the report page with all the relevant data
    return render(request, 'cfaa/report.html', {
        'query': query.text,  # Pass the query text to the template
        'report': report,  # Pass the current report object
        'query_reports': query_reports,  # Pass all reports for the timeline
        'page_obj': page_obj,  # Paginated related articles
        'paginator': paginator,  # Pass the paginator for navigation
    })






@csrf_exempt  # Since this is an AJAX request, we'll disable CSRF for this view (if not using CSRF tokens)
def monitor_question(request):
    env = environ.Env()
    environ.Env.read_env()

    # Get OpenAI API Key
    OPENAI_API_KEY = env('OPENAI_API_KEY')
    client = OpenAI(api_key=OPENAI_API_KEY)  # Instantiate the OpenAI client

    if request.method == 'POST':
        # Get the JSON data from the request body
        body = json.loads(request.body)
        query_text = body.get('query')  # Extract the query text
        query_id = body.get('query_id')

        # Fetch the query object
        query = Query.objects.get(id=query_id)

        # Create a new Topic object
        new_topic = Topic.objects.create(title=query_text)

        # Retrieve articles related to the query, including title and text
        articles = Article.objects.filter(query=query).values('id', 'title', 'text')

        # Generate a new report using the LLM call (no previous report, so pass None)
        updated_report_data = generate_updated_report(
            client,  # Pass the OpenAI client instance
            query.text,  # Pass the query text
            None,  # No previous report
            articles,  # Pass the articles (with title and text)
            max_tokens=1000,  # Increase max_tokens to 1000 for larger responses
            temperature=0,
            top_p=0
        )

        # Save the newly generated report and updates
        if updated_report_data["updated_summary"]:
            # Create the report in the database
            new_report = Report.objects.create(
                creation_day=date.today(),
                text=updated_report_data["updated_summary"],  # Use the generated report text
                basis="Initial basis",  # You can modify this as needed
                update=updated_report_data.get("updates", ""),  # Use the generated update text
                query=query,
                topic=new_topic
            )

            # Store each article in the ReportArticle model, with the current report
            for article_data in articles:
                article_id = article_data['id']
                article_instance = Article.objects.get(id=article_id)  # Get the actual Article instance

                # Create a ReportArticle instance for each article
                ReportArticle.objects.create(
                    report=new_report,
                    article=article_instance
                )

            # Return a success message as JSON
            return JsonResponse({
                'message': 'New topic created successfully!',
                'topic_id': new_topic.id,
                'report_id': new_report.id
            })

        # If report generation failed
        return JsonResponse({'error': 'Failed to generate report'}, status=500)

    # Return error if not POST request
    return JsonResponse({'error': 'Invalid request method'}, status=400)


