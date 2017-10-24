from django.contrib import admin

from .models import SatisfactionRating


@admin.register(SatisfactionRating)
class SatisfactionRatingAdmin(admin.ModelAdmin):
    list_display = (
        'customer_name',
        'score',
    )
