from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # path('home',views.featured_music, name='home'),
    path('search/', views.search_song, name='search'),
    path('<str:username>/', views.recommend_song, name='recommend_song'),
    path('<str:username>/recommend/', views.recommend, name='recommend'),
]

