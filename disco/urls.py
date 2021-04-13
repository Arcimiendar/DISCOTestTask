from django.urls import path

from disco.views import \
    empty_trash_view, extract_thumbnail_from_videofile_view, tracks_view, truncate_filename_view


urlpatterns = [
    path('empty-trash/', empty_trash_view),
    path('extract-thumbnail/', extract_thumbnail_from_videofile_view),
    path('tracks/', tracks_view),
    path('truncate-filename/', truncate_filename_view)
]
