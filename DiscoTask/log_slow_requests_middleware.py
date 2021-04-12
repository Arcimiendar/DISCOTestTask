import logging
import time
from django.conf import settings

logger = logging.getLogger(__name__)


class LogSlowRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.time_limit_for_request = \
            settings.TIME_LIMIT_FOR_REQUEST_BE_LOGGED if hasattr(settings, 'TIME_LIMIT_FOR_REQUEST_BE_LOGGED') else 60

    def __call__(self, request):
        request_start_time = time.time()

        response = self.get_response(request)

        request_time_end = time.time()

        duration = request_time_end - request_start_time

        if duration > self.time_limit_for_request:
            logger.warning(
                f'{request.method} {request.path} '
                f'GET: {dict(request.GET)} POST: {dict(request.POST)} request took {int(duration)} seconds'
            )

        return response
