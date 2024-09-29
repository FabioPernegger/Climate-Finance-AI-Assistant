import sqlite3

db_path = 'frontend/db.sqlite3'

def fetch_articles(year=None, month=None, query_id=None):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT cfaa_article.id, cfaa_article.title, cfaa_article.text
    FROM cfaa_article
    WHERE 1=1
    """

    params = []
    if year!=None:
        query += ' AND strftime(\'%Y\', cfaa_article.publish_date) = ?'
        params.append(year)
    if month!=None:
        query += ' AND strftime(\'%m\', cfaa_article.publish_date) = ?'
        params.append(month)
    if query_id!=None:
        query += ' AND query_id = ?'
        params.append(query_id)

    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()

    return results

def fetch_query(query_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''SELECT text
    FROM cfaa_query
    WHERE id = ?''', (query_id,))
    results = cursor.fetchone()

    conn.close()

    return results[0]

def store_summary(summary, article_id=None, date=None, query_id=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if article_id != None:
        query = "UPDATE cfaa_article SET summary = ? WHERE id = ?"
        cursor.execute(query, (summary, article_id))
    elif date != None:
        cursor.execute('''
                            INSERT INTO cfaa_summary (creation_date, text, query_id)
                            VALUES (?, ?, ?)
                            ''', (date, summary, query_id))

    conn.commit()
    conn.close()