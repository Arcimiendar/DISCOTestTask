from django.urls import path

from disco.views import empty_trash


urlpatterns = [
    path('empty_trash/', empty_trash),
]