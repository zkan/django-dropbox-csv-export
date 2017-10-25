from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Integration


class IntegrationTest(TestCase):
    def test_save_integration(self):
        User = get_user_model()
        user = User.objects.create(
            username='kan',
            password='12345',
            email='kan@pronto.com'
        )

        integration = Integration()
        integration.user = user
        integration.access_token = 'abc'
        integration.save()

        integration = Integration.objects.last()

        self.assertEqual(integration.user, user)
        self.assertEqual(integration.access_token, 'abc')
