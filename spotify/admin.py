
# Register your models here.
from django.contrib import admin
from .models import Track, PopTrack, HindiTrack,HipHopTrack,ChineseTrack,NepaliTrack,JapaneseTrack,RockTrack

admin.site.register(Track)
admin.site.register(PopTrack)
admin.site.register(HipHopTrack)
admin.site.register(HindiTrack)
admin.site.register(NepaliTrack)
admin.site.register(JapaneseTrack)
admin.site.register(ChineseTrack)
admin.site.register(RockTrack)
