from django.urls import path
from . import views
app_name = 'blogs'
urlpatterns = [
    path('', views.index, name='index'),
    path('posts/new/', views.post_new, name='post_new'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
]
