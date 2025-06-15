from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    path('', views.category_list, name='category_list'),
    # This URL pattern will be implemented later for task 4.2
    path('<slug:category_slug>/', views.topics_by_category, name='topics_by_category'),
]