from django.db import models


class SatisfactionRating(models.Model):
    customer_name = models.CharField(max_length=300)
    score = models.IntegerField()
