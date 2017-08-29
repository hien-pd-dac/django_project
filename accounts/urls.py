from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    url(r'^login/$', views.login_view, name='login'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^waitverify/$', views.waiting_verify_email, name='wait_verify_email'),
    url(r'^successverify/$', views.success_verify_email, name='success_verify_email'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^(?P<pk>\d+)/profile/$', views.UserProfileView.as_view(), name='profile'),
    url(r'^(?P<pk>\d+)/edit/$', views.ProfileEditView.as_view(), name='edit_profile'),
    url(r'^(?P<user_id>\d+)/vote/(?P<rating>\d+)/', views.vote_user_view, name='vote_user'),
    url(r'^seen/$', views.set_seen_noties, name='seen_noties'),
]
