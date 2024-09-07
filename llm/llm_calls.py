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