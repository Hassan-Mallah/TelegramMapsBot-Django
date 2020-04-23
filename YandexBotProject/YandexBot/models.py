from django.db import models
# Create your models here.


class SearchResult(models.Model):
    query = models.CharField(max_length=200)
    result = models.CharField(max_length=400)
    query_date = models.DateTimeField(auto_now_add=True)


class TelegramUser(models.Model):
    telegram_id = models.IntegerField()
    result_id = models.ForeignKey(SearchResult, on_delete=models.CASCADE)


class SearchAreas(models.Model):
    area = models.CharField(max_length=200)

    def __str__(self):
        return self.area
