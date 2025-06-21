from django.urls import path
from . import views

app_name = 'tagging'

urlpatterns = [
    path('', views.tag_list, name='tag_list'),
    path('suggestions/', views.tag_suggestions, name='tag_suggestions'),
    path('<slug:tag_slug>/', views.posts_by_tag, name='posts_by_tag'),
]
