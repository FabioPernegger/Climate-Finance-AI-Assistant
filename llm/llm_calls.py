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