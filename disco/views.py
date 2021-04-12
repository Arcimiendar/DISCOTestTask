from datetime import timedelta, datetime

from django.http import HttpResponse
from django.utils.timezone import now
from django.conf import settings

from disco.models import Track, Playlist, PlaylistVersion, TrackComment
from disco.utils import extract_last_non_blank_frame


def empty_trash(request):

    cutoff = now() - timedelta(days=settings.TRASH_DAYS)
    models = (
        Track, Playlist, PlaylistVersion, TrackComment,
    )
    count_work = 0
    for model in models:
        pks = model.objects\
            .filter(deleted__isnull=False)\
            .filter(hard_deleted__isnull=True)\
            .filter(deleted__lt=cutoff)\
            .values_list('pk', flat=True)[:settings.TRASH_BATCH_SIZE]
        count_work += pks.count()
        date = datetime.now()
        model.objects.filter(pk__in=pks).update(hard_deleted=date)
    return HttpResponse(f'hard deleted {count_work}')


def extract_thumbnail_from_videofile(request):
    extract_last_non_blank_frame(request.GET['videopath'])
    return HttpResponse(f'ok')
