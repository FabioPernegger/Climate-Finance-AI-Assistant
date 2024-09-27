from .models import Report, Article, ReportArticle
from datetime import date
from .llm_calls import generate_updated_report

def create_report(client, query, topic, articles, previous_report=None, max_tokens=1000, temperature=0, top_p=0):
    """
    Generates and saves a new report based on a query and list of articles.
    Optionally includes a previous report for updates.
    """

    # Generate the report using the LLM, passing previous_report if available
    updated_report_data = generate_updated_report(
        client,  # Pass the OpenAI client instance
        query.text,  # Pass the query text
        previous_report.text if previous_report else None,  # Pass previous report text or None
        list(articles),  # Pass the articles (with title and text)
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p
    )

    # Check if the report was successfully generated
    if updated_report_data.get("report"):
        # Create a new report in the database, setting the basis as the previous report if it exists
        new_report = Report.objects.create(
            creation_day=date.today(),
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
