from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # path('home',views.featured_music, name='home'),
    path('logout/', auth_views.LogoutView.as_view(next_page = '/home'), name='logout'),
    path('search/', views.search_song, name='search'),
    path('<str:username>/', views.recommend_song, name='recommend_song'),
    path('<str:username>/feedback/', views.submit_feedback, name='submit_feedback'),  # Add this line
    
]

