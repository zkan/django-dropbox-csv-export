import csv
import os

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from dropbox.dropbox import Dropbox
from dropbox.exceptions import ApiError, BadInputError
from dropbox.files import WriteMode
from dropbox.oauth import DropboxOAuth2Flow

from .models import SatisfactionRating
from integrations.models import Integration


APP_KEY = os.environ.get('APP_KEY', '')
APP_SECRET = os.environ.get('APP_SECRET', '')
PATH = '/simplesat'


@login_required
def index(request):
    context = {
        'data': [],
        'files': [],
        'errors': []
    }

    try:
        integration = Integration.objects.get(
            user=request.user
        )
        db = Dropbox(integration.access_token)
    except Integration.DoesNotExist as e:
        db = None
        context['errors'].append(e.__str__())

    if db:
        try:
            db.files_create_folder(PATH)
        except ApiError as e:
            context['errors'].append(e.error)
        except BadInputError as e:
            context['errors'].append(e.body)

        try:
            entries = db.files_list_folder(PATH).entries
            for each in entries:
                context['files'].append(each.name)
        except ApiError as e:
            context['errors'].append(e.error)
        except BadInputError as e:
            context['errors'].append(e.body)

    return render(
        request,
        'index.html',
        {
            'context': context
        }
    )


def get_dropbox_auth_flow(web_app_session):
    redirect_uri = 'https://c64fc520.ngrok.io/satisfaction-ratings/' \
        'dropbox-auth-finish/'
    return DropboxOAuth2Flow(
        APP_KEY,
        APP_SECRET,
        redirect_uri,
        web_app_session,
        'dropbox-auth-csrf-token'
    )


@login_required
def dropbox_sync(request):
    try:
        integration = Integration.objects.get(
            user=request.user
        )
        db = Dropbox(integration.access_token)
    except Integration.DoesNotExist as e:
        db = None

    if db:
        file_name = 'feedback.csv'

        satisfaction_ratings = SatisfactionRating.objects.all()
        rows = [
            (each.customer_name, each.score)
            for each in satisfaction_ratings
        ]
        with open(file_name, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['Customer Name', 'Score'])
            writer.writerows(rows)

        with open(file_name, 'rb') as f:
            db.files_upload(
                f.read(),
                PATH + '/' + file_name,
                mode=WriteMode('overwrite')
            )

    return HttpResponseRedirect(reverse('index'))


@login_required
def dropbox_auth_start(request):
    authorize_url = get_dropbox_auth_flow(request.session).start()
    return HttpResponseRedirect(authorize_url)


@login_required
def dropbox_auth_finish(request):
    oauth_result = get_dropbox_auth_flow(request.session).finish(
        request.GET
    )
    try:
        integration = Integration.objects.get(
            user=request.user
        )
        integration.access_token = oauth_result.access_token
        integration.save()
    except Integration.DoesNotExist:
        Integration.objects.create(
            user=request.user,
            access_token=oauth_result.access_token
        )

    return HttpResponseRedirect(reverse('index'))


@login_required
def revoke(request):
    try:
        integration = Integration.objects.get(
            user=request.user
        )
        db = Dropbox(integration.access_token)
        db.auth_token_revoke()
        integration.delete()
    except Integration.DoesNotExist:
        pass

    return HttpResponseRedirect(reverse('index'))
