# admin.py
from django.contrib import admin
from .models import Feedback, Playlist, Track

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'algorithm', 'user_age_group', 'user_favorite_genre', 'feedback_date')
    search_fields = ('user__username', 'algorithm', 'user__user_preferences__age_group', 'user__user_preferences__favorite_music_genre')

admin.site.register(Feedback, FeedbackAdmin)

class TrackInline(admin.StackedInline):
    model = Track
    extra = 0

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [TrackInline]

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist_name', 'album_name', 'playlist')
    list_filter = ('playlist', 'artist_name', 'album_name')
