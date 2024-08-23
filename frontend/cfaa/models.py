from django.db import models

class NewsArticle(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Report(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    related_articles = models.ManyToManyField(NewsArticle, related_name='reports')
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
