# generates a summary, relevant to a query based on the input of an article (broken down into title and text)
from openai import OpenAI
from pydantic import BaseModel
from typing import List

def generate_summary(client, query, title, text, max_tokens=200, temperature=0, top_p=0):
    system_prompt = '''Summarize the article you are provided with in 2-3 very short sentences. The article consists 
    of a TITLE and a TEXT. The summary should contain the main information, also with regard to the given QUERY but 
    without answering it directly. Do not use introductory phrases (i.e., the article discusses) but directly start.'''
    # system_prompt = '''Extract the passage in the given text that is most relevant to the given query. It should be
    # only 2-3 sentences.'''
    user_prompt = f'QUERY: {query}, TITLE: {title}, TEXT: {text}'

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p
    )

    return response.choices[0].message.content


# generates a summary based on multiple articles in order to answer a query
def generate_summary_over_articles(client, query, articles, max_tokens=300, temperature=0, top_p=0.5):
    system_prompt = f'''You are provided with a QUERY and multiple articles (ARTICLE 1, ARTICLE 2, etc.). Write a concise summary of 3-5 sentences that captures the general opinion regarding the 
    query. Start with the most pertinent information directly, avoiding any introductory phrases or 
    general background. Ensure that the summary is focused on the key insights and opinions drawn from the articles and relevant to the query.'''

    user_prompt = f'QUERY: {query}'
    for i, article in enumerate(articles):
        user_prompt += f', ARTICLE {i + 1}: {article}'

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p
    )

    return response.choices[0].message.content


# generates an opionion (0-100) in order to graph it over time.
def generate_opinion(client, query, summary, max_tokens=200, temperature=0, top_p=0):
    system_prompt = '''Analyse the text below and give back a number between 0-100 indicating how strongly the text agrees or disagrees
    with the query. 0 means that the text confidently answers the query negatively, while 100 means it is confidently positive.
    do not contain anything other than the number in your response.'''
    user_prompt = f'QUERY: {query}, TEXT: {summary}'

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p
    )

    return response.choices[0].message.content


# generates a forecast to graph it on a pie chart and generates reasoning.
# Output is in this format: xx positive// xx negative //xx neutral// forecast reasoning where xx represents percentages
def generate_forecast(client, query, text, max_tokens=200, temperature=0, top_p=0):
    system_prompt = '''Analyse the text below and create a forecast which answers the query by predicting whether
    the sentiment is going to be positive, negative or neutral. Please format your answer by providing a number 
    between 0-100 for each positive, negative and neutral which indicates the percentage likelihood of each in the future.
    The sum should of all likelihoods should add up to 100. Please also include a brief explenation explaining the reasoning 
    behind the forecast. Format your answer in this way:
    xx positive// xx negative// xx neutral// forecast reasoning.

    Where xx is the percentage likelihood.'''
    user_prompt = f'QUERY: {query}, TEXT: {text}'

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p
    )

    return response.choices[0].message.content


# generate an updated report
class UpdatedReport(BaseModel):
    report: str
    updates: str

def generate_updated_report(client: OpenAI, query: str, previous_report: str, articles: List[dict], max_tokens=2000, temperature=0, top_p=0):
    """
    Generates an updated report based on a query, articles (with title and text), and optionally a previous report.
    If no previous report is provided, generates a new report based solely on the articles.
    """

    # Prepare the system prompt depending on whether there is a previous report
    if previous_report:
        system_prompt = '''You receive as input a QUERY, a PREVIOUS REPORT, and a list of ARTICLES.
        Create a report in HTML structure, mainly based on the ARTICLES and partly on the PREVIOUS REPORT,
        focus heavily on the ARTICLES and do not base the new report on the PREVIOUS REPORT, also do 
        not base it on your existing knowledge.
        The Aim of the report is to extract the most important information Of the ARTICLES and PREVIOUS REPORT 
        and display it in a structured way to adress the QUERY. Use HTML to structure the report well, using 
        bulletpoints, bold text and headlines. Return this report as the "report", make sure the report 
        does not get too long.
        Compare the PREVIOUS REPORT with the new information gained from the ARTICLES, gather all the changes
        and compile them also with HTML (same formatting) into a concise Update with some important bulletpoints.
        Return this update in "updates". Do not include a title for the updates.'''
    else:
        system_prompt = '''You receive as input a QUERY and a list of ARTICLES. 
        Create a report based on only the ARTICLES, not on your existing knowledge. The Aim of the 
        report is to extract the most important information Of the ARTICLES and 
        display it in a structured way to adress the QUERY. Use HTML to structure the report well, using 
        bulletpoints, bold text and headlines, with all important insights that are provided by ARTICLES.
        Return this report as the "report".'''   

    # Prepare the user prompt, including both article titles and truncated text
    articles_text = "\n".join([f"ARTICLE {article['id']}: {article['title'][:500]}: {article['text'][:500]}" for article in articles[:5]])
    user_prompt = f'QUERY: {query}\nPREVIOUS REPORT: {previous_report or "None"}\nARTICLES: {articles_text}'

    try:
        # Make the API call to generate the updated report and changes
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=UpdatedReport,  # Use Pydantic model for structured output
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )

        # Extract the structured response
        structured_response = completion.choices[0].message.parsed

        return {
            "report": structured_response.report,
            "updates": structured_response.updates if structured_response.updates != None else 'No updates yet.',
        }

    except Exception as e:
        print(f"Error generating report: {e}")
        return {
            "report": None,
            "updates": None,
        }



# cuts out an important passage fomr an article, relevant to a query based on the input of an article (broken down into title and text)
def generate_passage(client, query, title, text, max_tokens=200, temperature=0, top_p=0):
    system_prompt = '''Extract a relevant passage of about 50-100 words based on this article. The article consists 
    of a TITLE and a TEXT. The passage should contain the main information, with regard to the given QUERY but 
    without answering it directly. Do not use introductory phrases (i.e., the article discusses) but directly start.'''
    user_prompt = f'QUERY: {query}, TITLE: {title}, TEXT: {text}'

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p
    )

    return response.choices[0].message.content