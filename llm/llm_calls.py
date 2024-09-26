# generates a summary, relevant to a query based on the input of an article (broken down into title and text)
def generate_summary(client, query, title, text, max_tokens = 200, temperature = 0, top_p = 0):

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

#generates a summary based on multiple articles in order to answer a query
def generate_summary_over_articles(client, query, articles, max_tokens = 200, temperature = 0, top_p = 0.5):

    system_prompt = f'''You are provided with a QUERY and multiple articles (ARTICLE 1, ARTICLE 2, etc.) from a 
    certain time period. Write a concise summary of 3-5 sentences that captures the general opinion regarding the 
    query during this time. Start with the most pertinent information directly, avoiding any introductory phrases or 
    general background. Ensure that the summary is focused on the key insights and opinions drawn from the articles.'''

    user_prompt = f'QUERY: {query}'
    for i, article in enumerate(articles):
        if i > 5:
            break
        user_prompt += f', ARTICLE {i+1}: {article}'

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
def generate_opinion(client, query, summary, max_tokens = 200, temperature = 0, top_p = 0):

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
def generate_forecast(client, query, text, max_tokens = 200, temperature = 0, top_p = 0):

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
def generate_updated_report(client, query, report, articles, max_tokens = 200, temperature = 0, top_p = 0):

    system_prompt = '''Take an input of a query, a Report and articles. Create an updated 
    report (based on the query) in html format, correcting and completing any information it is missing 
    based on the articles. Return this updated report as the "updated_summary" in 
    the output json. Afterwards gather all the changes done on the report and create 
    a list, in html format, containing all the changes done to update the report. 
    Return this list in "updates" in the output json. Lastly create a ranking of 
    articles based on their importance in terms of creating an updated report. Return 
    this ranking by returning the article id's in order of most important to least 
    important in the "article_relevance" array, with the most important article id 
    being in article_relevance[0].'''
    user_prompt = f'QUERY: {query}, REPORT: {report}, articles: {articles}'

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        response_format={ 
            "type": "json_schema",
            "strict": True, 
            "json_schema":{
                "name": "Updated_Report",
                "schema": {
                    "type": "object",
                    "properties": {
                    "updated_summary": {
                        "type": "string"
                    },
                    "updates": {
                        "type": "string"
                    },
                    "article_relevance": {
                        "type": "array",
                        "items": {
                        "type": "string"
                        }
                    }
                    },
                    "required": []
                }
            }
        }
    )

    return response.choices[0].message.content


def generate_updated_report_new(client, query, previous_report, articles, max_tokens=200, temperature=0, top_p=0):

    # Prepare the system prompt depending on whether there is a previous report
    if previous_report:
        system_prompt = '''Take an input of a query, a previous report, and a list of articles. 
        Create an updated report based on the query, correcting and completing any missing information 
        based on the articles. Return this updated report as the "updated_summary" in the output JSON.
        Then, gather all the changes done to the report and create a list (in HTML format) containing 
        the changes made to update the report. Return this list in "updates" in the output JSON.
        Lastly, rank the articles based on their importance in updating the report. Return the article IDs 
        in order of relevance, with the most important being in "article_relevance".'''
    else:
        system_prompt = '''Take an input of a query and a list of articles. Create a new report based on 
        the query using the articles. Return this report as the "updated_summary" in the output JSON.
        Lastly, rank the articles based on their importance in generating the report. Return the article 
        IDs in order of relevance in "article_relevance".'''

    # Prepare the user prompt
    articles_text = "\n".join([f"Article {article['id']}: {article['text']}" for article in articles])
    user_prompt = f'QUERY: {query}\nPREVIOUS REPORT: {previous_report or "None"}\nARTICLES: {articles_text}'

    try:
        # Make the API call to generate the updated report and changes
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            response_format="json",
            json_schema={
                "type": "object",
                "properties": {
                    "updated_summary": {"type": "string"},
                    "updates": {"type": "string"},
                    "article_relevance": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["updated_summary", "article_relevance"]
            }
        )

        # Extract the structured response content
        result = response.choices[0].message.content

        # Ensure the result has the necessary fields
        report_data = result.get("updated_summary", "")
        updates = result.get("updates", "")
        article_relevance = result.get("article_relevance", [])

        return {
            "updated_summary": report_data,
            "updates": updates,
            "article_relevance": article_relevance
        }

    except Exception as e:
        print(f"Error generating report: {e}")
        return {
            "updated_summary": None,
            "updates": None,
            "article_relevance": []
        }

# cuts out an important passage fomr an article, relevant to a query based on the input of an article (broken down into title and text)
def generate_passage(client, query, title, text, maxg_tokens = 200, temperature = 0, top_p = 0):

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