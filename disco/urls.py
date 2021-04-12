from django.urls import path

from disco.views import empty_trash, extract_thumbnail_from_videofile


urlpatterns = [
    path('empty_trash/', empty_trash),
    path('extract_thumbnail/', extract_thumbnail_from_videofile),
]