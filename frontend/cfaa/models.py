from django.db import models

class Query(models.Model):
    text = models.TextField()
    search_query = models.TextField()
    article_summary = models.TextField()

    def __str__(self):
        return self.text

class Article(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name='articles')
    publish_date = models.DateField()
    title = models.TextField()
    text = models.TextField()
    url = models.URLField()
    summary = models.TextField(null=True, blank=True)  # Assuming summary/retrieved passage

    def __str__(self):
        return self.title

class Topic(models.Model):
    title = models.CharField(max_length=255)
    articles = models.ManyToManyField(Article, related_name='topics')

    def __str__(self):
        return self.title

class Report(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name='reports')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='reports')
    creation_day = models.DateField()
    text = models.TextField()
    basis = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='derived_reports')
    update = models.TextField()

    def __str__(self):
        return f"Report on {self.creation_day}"

class Summary(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name='summaries')
    creation_date = models.DateField()
    text = models.TextField()

    def __str__(self):
        return f"Summary created on {self.creation_date}"

class ReportArticle(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='report_articles')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='report_articles')

    def __str__(self):
        return f"ReportArticle for {self.report} and {self.article}"
