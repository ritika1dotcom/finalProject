from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # path('home',views.featured_music, name='home'),
    path('fetch',views.fetch_music, name='fetch'),
    path('search/', views.search_song, name='search'),
    path('<str:username>/', views.recommend_song, name='recommend_song'),
    path('<str:username>/preference/', views.user_preferences_view, name = 'user_has_preference'),
    path('<str:username>/update_song_rating/', views.update_song_rating, name='update_song_rating'),
    path('<str:username>/feedback/', views.submit_feedback, name='submit_feedback'),  # Add this line
    
]

