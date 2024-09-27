from .models import Report, Article, ReportArticle
from datetime import date
from .llm_calls import generate_updated_report
from .scraper import scrape_and_store_news

def create_report(client, query, topic, articles, previous_report=None, creation_date=date.today(), max_tokens=1000, temperature=0, top_p=0):
    """
    Generates and saves a new report based on a query and list of articles.
    Optionally includes a previous report for updates.
    """

    # Generate the report using the LLM, passing previous_report if available
    updated_report_data = generate_updated_report(
        client,  # Pass the OpenAI client instance
        query.text,  # Pass the query text
        previous_report.text if previous_report else None,  # Pass previous report text or None
        articles,  # Pass the articles (with title and text)
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p
    )

    # Check if the report was successfully generated
    if updated_report_data.get("report"):
        # Create a new report in the database, setting the basis as the previous report if it exists
        new_report = Report.objects.create(
            creation_day=creation_date,
            text=updated_report_data["report"],  # Use the generated report text
            basis=previous_report,  # Set the basis as the previous report if it exists
            update=updated_report_data.get("updates", ""),  # Use the generated update text
            query=query,
            topic=topic
        )

        # Store each article in the ReportArticle model
        for article_data in articles:
            article_instance = Article.objects.get(id=article_data['id'])  # Get the actual Article instance

            # Create a ReportArticle instance for each article
            ReportArticle.objects.create(
                report=new_report,
                article=article_instance,
            )

        return new_report

    # If the report generation failed
    raise Exception("Failed to generate report")


from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # To easily manage months
from .models import Query, Report, Article, Topic, ReportArticle  # Import necessary models


def generate_reports_for_last_six_months(client, query_text, search_query, topic):
    """
    Generates six monthly reports for the last six months.
    The first report is generated from scratch, and subsequent reports use the previous report as the basis.

    Args:
        client (OpenAI): The OpenAI client instance.
        query_text (str): The query text to generate reports.
        search_query (str): The refined search query used in scraping news articles.
        topic (Topic): The topic under which reports are being created.

    Returns:
        list: A list of generated reports.
    """

    today = datetime.now()
    previous_report = None  # No previous report for the first iteration
    reports = []  # To store the generated reports

    # Loop over the last 6 months
    for i in reversed(range(6)):
        # Calculate the start and end date for the month
        end_date = today - relativedelta(months=i)
        start_date = end_date - relativedelta(months=1)

        # Convert dates to the format 'YYYY-MM-DD'
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # Scrape news articles for the current month
        print(f"Scraping articles from {start_date_str} to {end_date_str}...")
        scrape_query = f"{search_query} after:{start_date_str} before:{end_date_str}"
        scrape_and_store_news(query_text, scrape_query, start_date=start_date, end_date=end_date)

        # Fetch the articles scraped in this date range for the query
        query = Query.objects.get(text=query_text)
        articles = Article.objects.filter(query=query, publish_date__range=[start_date_str, end_date_str]).values('id',
                                                                                                                  'title',
                                                                                                                  'text')

        # If there are no articles, skip this month
        if not articles:
            print(f"No articles found for {start_date_str} to {end_date_str}")
            continue

        # Create a new report based on the scraped articles
        print(f"Creating report for {start_date_str} to {end_date_str}...")
        report = create_report(
            client=client,
            query=query,
            topic=topic,
            articles=articles,
            previous_report=previous_report,  # Use previous report as the basis
            creation_date=end_date,
            max_tokens=1000,
            temperature=0,
            top_p=0
        )

        # Set the new report as the previous report for the next iteration
        previous_report = report

        # Append the generated report to the list
        reports.append(report)

    return reports

