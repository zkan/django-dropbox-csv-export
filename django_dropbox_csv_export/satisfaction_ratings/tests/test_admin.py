from django.contrib.auth.models import User
from django.test import TestCase

from ..models import SatisfactionRating


class SatisfactionRatingAdminTest(TestCase):
    def setUp(self):
        User.objects.create_superuser('admin', 'admin@pronto.com', 'admin')
        self.client.login(username='admin', password='admin')

        self.url = '/admin/satisfaction_ratings/satisfactionrating/'

    def test_access_satisfaction_rating_admin_should_have_columns(self):
        SatisfactionRating.objects.create(
            customer_name='Pronto',
            score=9
        )
        response = self.client.get(self.url)

        expected = '<div class="text"><a href="?o=1">Customer name</a></div>'
        self.assertContains(response, expected, count=1, status_code=200)

        expected = '<div class="text"><a href="?o=2">Score</a></div>'
        self.assertContains(response, expected, count=1, status_code=200)
