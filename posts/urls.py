from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views
app_name = 'posts'

urlpatterns = [
    url(r'^(?P<pk>\d+)/create/$', views.UserCreatePostView.as_view(), name='create_post'),
    url(r'^(?P<pk>\d+)/detail/$', views.DetailPostView.as_view(), name='detail_post'),
    url(r'^(?P<pk>\d+)/edit/$', views.EditPostView.as_view(), name='edit_post'),
    url(r'^(?P<pk>\d+)/delete/$', views.DeletePostView.as_view(), name='delete_post'),
    url(r'^(?P<post_id>\d+)/like/$', views.like, name='like_post'),
    url(r'^(?P<post_id>\d+)/comment/$', views.comment_on_post, name='comment_post'),
    url(r'^(?P<post_id>\d+)/comment/(?P<comment_id>\d+)/edit/$', views.edit_comment, name='edit_comment'),
    url(r'^(?P<post_id>\d+)/comment/(?P<comment_id>\d+)/delete/$', views.delete_comment, name='delete_comment'),
    url(r'^search/$', views.search_post_view, name='search_post'),
    url(r'^approve/$', views.admin_approve_post_view, name='approve'),
    url(r'^approve_post/(?P<pk>\d+)/$', views.admin_approve_post, name='approve_post'),
    url(r'^caculate_approve/$', views.caculate_approve, name='caculate_approve'),
]
