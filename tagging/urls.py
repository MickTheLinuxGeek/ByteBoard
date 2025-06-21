from django.urls import path
from . import views

app_name = 'tagging'

urlpatterns = [
    path('suggestions/', views.tag_suggestions, name='tag_suggestions'),
]