from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='base.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page = '/home'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('preferences/', views.preferences_view, name='preferences'),
    path('add_song_history/', views.add_song_history, name='add_song_history'),
    path('<str:username>/', views.user_song_history, name='user_song_history'),
]  
