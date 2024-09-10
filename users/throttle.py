import logging

from rest_framework.throttling import SimpleRateThrottle
from django.core.cache import cache

logger=logging.getLogger('users')

class LoginRateThrottle(SimpleRateThrottle):
    scope = 'login'

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return f'login_attempt_user_{request.user.id}'
        else:
            ip_address = request.META.get('REMOTE_ADDR')
            return f'login_attempt_anon_{ip_address}'

    def allow_request(self, request, view):
        block_time = 15 * 60
        if request.user.is_authenticated:
            max_attempts = 20
        else:
            max_attempts = 5

        cache_key = self.get_cache_key(request, view)
        if cache_key:
            attempts = cache.get(cache_key, 0)
            if attempts >= max_attempts:
                wait_time = cache.ttl(cache_key) or 0
                if wait_time > 0:
                    logger.warning(f"Rate limit exceeded for {request.user} (IP: {request.META.get('REMOTE_ADDR')})."
                                   f" Waiting time: {wait_time} seconds.")
                    return False

            cache.set(cache_key, attempts + 1, timeout=block_time)
            logger.info(f"Login attempt {attempts + 1} for {request.user} (IP: {request.META.get('REMOTE_ADDR')}).")
        return True

    def wait(self):
            return 15 * 60




