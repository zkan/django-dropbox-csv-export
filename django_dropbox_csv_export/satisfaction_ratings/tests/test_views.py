from unittest.mock import call, MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase

from dropbox.files import WriteMode

from ..views import get_dropbox_auth_flow
from integrations.models import Integration


class SatisfactionRatingIndexViewTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            'kan',
            'kan@pronto.com',
            'pass'
        )

    def test_index_view_should_require_login(self):
        response = self.client.get(reverse('index'))
        self.assertRedirects(
            response,
            f'/?next={reverse("index")}',
            status_code=302,
            target_status_code=404
        )

    def test_index_view_should_render_text_as_expected(self):
        self.client.login(username='kan', password='pass')
        response = self.client.get(reverse('index'))

        expected = '<h1>Dropbox Integration</h1>'
        self.assertContains(response, expected, status_code=200)

        expected = 'Files: []'
        self.assertContains(response, expected, status_code=200)

        expected = 'Errors [&#39;Integration matching query does not ' \
            'exist.&#39;]'
        self.assertContains(response, expected, status_code=200)

        expected = f'<a href="{reverse("dropbox_sync")}">' \
            'Sync Data</a>'
        self.assertContains(response, expected, status_code=200)

        expected = f'<a href="{reverse("dropbox_auth_start")}">' \
            'Authenticate</a> |'
        self.assertContains(response, expected, status_code=200)

        expected = f'<a href="{reverse("dropbox_auth_revoke")}">' \
            'Revoke</a>'
        self.assertContains(response, expected, status_code=200)

    def test_index_view_with_no_integration_should_not_call_dropbox(self):
        self.client.login(username='kan', password='pass')

        with patch('satisfaction_ratings.views.Dropbox') as mock:
            self.client.get(reverse('index'))
            self.assertEqual(mock.call_count, 0)

    def test_index_view_with_integration_should_render_and_call_dropbox(self):
        integration = Integration.objects.create(
            user=self.user,
            access_token='abc'
        )
        self.client.login(username='kan', password='pass')

        with patch('satisfaction_ratings.views.Dropbox') as mock:
            db = mock.return_value

            response = self.client.get(reverse('index'))

            expected = 'Errors []'
            self.assertContains(response, expected, status_code=200)

            mock.assert_called_once_with(integration.access_token)
            db.files_create_folder.assert_called_once_with('/simplesat')
            db.files_list_folder.assert_called_once_with('/simplesat')


class DropboxOAuthTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            'kan',
            'kan@pronto.com',
            'pass'
        )

    def test_get_dropbox_auth_flow_should_call_dropbox_oauth_2_flow(self):
        redirect_uri = reverse('dropbox_auth_finish')

        with patch('satisfaction_ratings.views.DropboxOAuth2Flow') as mock:
            get_dropbox_auth_flow('session')

            mock.assert_called_once_with(
                '',
                '',
                redirect_uri,
                'session',
                'dropbox-auth-csrf-token'
            )

    def test_dropbox_sync_view_should_require_login(self):
        response = self.client.get(reverse('dropbox_sync'))
        self.assertRedirects(
            response,
            f'/?next={reverse("dropbox_sync")}',
            status_code=302,
            target_status_code=404
        )

    def test_dropbox_sync_should_write_csv_and_upload_to_dropbox_then_redirect(
        self
    ):
        file_name = 'feedback.csv'
        integration = Integration.objects.create(
            user=self.user,
            access_token='abc'
        )
        self.client.login(username='kan', password='pass')

        with patch('satisfaction_ratings.views.Dropbox') as mock:
            with patch('satisfaction_ratings.views.open') as mock_open:
                db = mock.return_value

                response = self.client.get(reverse('dropbox_sync'))

                self.assertRedirects(
                    response,
                    reverse('index'),
                    status_code=302,
                    target_status_code=200
                )

                calls = [
                    call(integration.access_token),
                    call(integration.access_token),
                ]
                for each in calls:
                    self.assertTrue(each in mock.mock_calls)

                db.files_upload.assert_called_once_with(
                    mock_open.return_value.__enter__.return_value.read(),
                    f'/simplesat/{file_name}',
                    mode=WriteMode('overwrite', None)
                )

                calls = [
                    call(file_name, 'w'),
                    call(file_name, 'rb'),
                ]
                for each in calls:
                    self.assertTrue(each in mock_open.mock_calls)

    def test_dropbox_auth_start_should_get_auth_flow_and_redirect(self):
        self.client.login(username='kan', password='pass')

        with patch('satisfaction_ratings.views.get_dropbox_auth_flow') as mock:
            authorize_url = 'api.dropbox.com'
            mock.return_value.start.return_value = authorize_url

            response = self.client.get(reverse('dropbox_auth_start'))

            self.assertRedirects(
                response,
                reverse('dropbox_auth_start') + authorize_url,
                status_code=302,
                target_status_code=200,
                fetch_redirect_response=False
            )

            self.assertTrue(mock.called)
            self.assertTrue(mock.return_value.start.called)

    def test_dropbox_auth_finish_should_finish_auth_flow_and_redirect(self):
        self.client.login(username='kan', password='pass')

        with patch('satisfaction_ratings.views.get_dropbox_auth_flow') as mock:
            mock_oauth_result = MagicMock()
            mock_oauth_result.access_token = 'abc'
            mock.return_value.finish.return_value = mock_oauth_result

            response = self.client.get(reverse('dropbox_auth_finish'))

            self.assertRedirects(
                response,
                reverse('index'),
                status_code=302,
                target_status_code=200,
                fetch_redirect_response=False
            )

            self.assertTrue(mock.called)
            self.assertTrue(mock.return_value.finish.called)

            integration = Integration.objects.last()

            self.assertEqual(integration.user, self.user)
            self.assertEqual(integration.access_token, 'abc')

    def test_dropbox_revoke_should_finish_auth_flow_and_redirect(self):
        integration = Integration.objects.create(
            user=self.user,
            access_token='abc'
        )
        self.client.login(username='kan', password='pass')

        with patch('satisfaction_ratings.views.Dropbox') as mock:
            db = mock.return_value

            response = self.client.get(reverse('dropbox_auth_revoke'))

            self.assertRedirects(
                response,
                reverse('index'),
                status_code=302,
                target_status_code=200,
                fetch_redirect_response=False
            )

            self.assertEqual(Integration.objects.count(), 0)

            mock.assert_called_once_with(integration.access_token)
            db.auth_token_revoke.assert_called_once_with()
