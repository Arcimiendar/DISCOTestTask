from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now


class SoftDeleteMixin(models.Model):
    deleted = models.DateTimeField(blank=True, null=True)
    hard_deleted = models.DateTimeField(blank=True, null=True)

    def delete(self, *args, **kwargs):
        self.deleted = now()
        self.save(update_fields=['deleted'])

    class Meta:
        abstract = True


class PlaylistVersion(SoftDeleteMixin):
    version = models.FloatField(default=0)


class Playlist(SoftDeleteMixin):
    title = models.CharField(max_length=20)
    number_of_tracks = models.PositiveIntegerField(default=0)
    version = models.ForeignKey(PlaylistVersion, on_delete=models.CASCADE)


class TrackComment(SoftDeleteMixin):
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='track_comment')
    text = models.TextField(max_length=250)


class Business(models.Model):
    hostname = models.CharField(max_length=20)


class Artwork(models.Model):
    album = models.CharField(max_length=20)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='artwork')


class Track(SoftDeleteMixin):
    title = models.CharField(max_length=20)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='track')
    comment = models.ForeignKey(TrackComment, on_delete=models.CASCADE, related_name='track')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='track')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='track')
    artist = models.CharField(max_length=20)
    name = models.CharField(max_length=20)


class EventObject(models.Model):
    event_object_track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='eventobjects')


class Event(models.Model):
    name = models.CharField(max_length=20)
    timestamp = models.DateTimeField()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='event')
    event_object = models.ForeignKey(EventObject, on_delete=models.CASCADE, related_name='event')
