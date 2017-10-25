from django.conf import settings
from django.db import models


class Integration(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL
    )
    access_token = models.CharField(max_length=500)
