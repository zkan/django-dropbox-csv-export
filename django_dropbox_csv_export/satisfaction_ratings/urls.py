from django.conf.urls import url

from .views import (
    index,
    dropbox_auth_start,
    dropbox_auth_finish,
    dropbox_sync,
    revoke,
)


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'dropbox-sync/$',
        dropbox_sync, name='dropbox_sync'),
    url(r'dropbox-auth-start/$',
        dropbox_auth_start, name='dropbox_auth_start'),
    url(r'dropbox-auth-finish/$',
        dropbox_auth_finish, name='dropbox_auth_finish'),
    url(r'dropbox-auth-revoke/$',
        revoke, name='dropbox_auth_revoke'),
]
