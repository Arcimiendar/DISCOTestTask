import json

from datetime import timedelta, datetime

from django.db.models import Q, Count, Case, When
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


def tracks(request):
    if 'sort' in request.GET:
        sort = json.loads(request.GET['sort'])
    else:
        sort = ['-play_count', '-download_count', 'artist', 'name']
    # if 'pitch_count' in sort or '-pitch_count' in sort:
    #     return self.tracks_vs_playlists(request, sort)
    # from_date, to_date = self._get_from_to(request)
    from_date, to_date = datetime.now(), datetime.now()
    user_type = request.GET.get('user_type', 'staff')
    filter_prop = request.GET.get('filter_prop')
    play_q = Q(eventobjects__event__name='play_track')
    download_q = Q(eventobjects__event__name='download_track')
    time_q = Q()
    if from_date:
        time_q &= Q(eventobjects__event__timestamp__gte=from_date)
    if to_date:
        time_q &= Q(eventobjects__event__timestamp__lte=to_date)
    # business_user_ids = self._business_user_ids()
    business_user_ids = [
        1, 138, 139, 141, 148, 154, 161, 162, 163,
        185, 186, 190, 215, 90, 94, 95, 96, 98,
        1219, 124, 224, 283, 224, 220
    ]
    user_type_q = Q(eventobjects__event__user_id__in=business_user_ids)
    user_q = Q()
    if user_type == 'staff':
        user_q = user_type_q
    elif user_type == 'client':
        user_q = ~user_type_q
    if filter_prop in ('play_count', 'download_count', 'playlist_count'):
        filter_q = Q(**{'{}__gt'.format(filter_prop): 0})
    else:
        filter_q = Q(all_count__gt=0)

    ts = Track.objects.all().filter(time_q & ((play_q & user_q) | download_q))\
        .annotate(
            play_count=Count(Case(When(play_q, then=1))),
            download_count=Count(Case(When(download_q, then=1))),
            all_count=Count(Case(When(play_q | download_q, then=1))),
        )\
        .filter(filter_q)\
        .order_by(*sort)
    offset = json.loads(request.GET.get('offset', '0'))
    count = json.loads(request.GET.get('count', '10'))
    # ts = TrackStatsSerializer.setup_eager_loading(ts)
    # serializer = TrackStatsSerializer(
    #     ts[offset:offset+count],
    #     many=True,
    #     context={'request': request}
    # )
    # return Response(serializer.data)
    return HttpResponse("ok")
