from django.db import models

class Query(models.Model):
    text = models.TextField()
    search_query = models.TextField()

    def __str__(self):
        return self.text

class Article(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    publish_date = models.DateField()
    title = models.TextField()
    text = models.TextField()
    url = models.URLField()

    def __str__(self):
        return self.title
