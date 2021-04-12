from django.contrib import admin
from disco.models import Track, TrackComment, Playlist, PlaylistVersion

admin.site.register(TrackComment)
admin.site.register(Track)
admin.site.register(Playlist)
admin.site.register(PlaylistVersion)
# Register your models here.
