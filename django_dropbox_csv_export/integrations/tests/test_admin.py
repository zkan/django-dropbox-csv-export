from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Integration


class IntegrationAdminTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            'admin',
            'admin@pronto.com',
            'admin'
        )
        self.client.login(username='admin', password='admin')

        self.url = '/admin/integrations/integration/'

    def test_access_integration_admin_should_have_columns(self):
        Integration.objects.create(
            user=self.user,
            access_token='abcd'
        )
        response = self.client.get(self.url)

        expected = '<div class="text"><a href="?o=1">User</a></div>'
        self.assertContains(response, expected, count=1, status_code=200)

        expected = '<div class="text"><a href="?o=2">Access token</a></div>'
        self.assertContains(response, expected, count=1, status_code=200)
