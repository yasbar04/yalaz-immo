import time
import threading
from collections import defaultdict

from django.http import HttpResponse
from django.conf import settings


_rate_limit_store = defaultdict(list)
_rate_limit_lock = threading.Lock()

RATE_LIMIT_RULES = {
    '/contact/': (10, 300),       # 10 requests per 5 minutes
    '/sell/': (5, 300),           # 5 requests per 5 minutes
    '/accounts/login/': (10, 60), # 10 attempts per minute
    '/accounts/signup/': (5, 60), # 5 signups per minute
}

DEFAULT_RATE = (120, 60)          # 120 req/min for all other paths


def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '')


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST':
            ip = _get_client_ip(request)
            path = request.path_info

            limit, window = DEFAULT_RATE
            for prefix, rule in RATE_LIMIT_RULES.items():
                if path.startswith(prefix):
                    limit, window = rule
                    break

            key = f'{ip}:{path}'
            now = time.time()

            with _rate_limit_lock:
                timestamps = _rate_limit_store[key]
                cutoff = now - window
                _rate_limit_store[key] = [t for t in timestamps if t > cutoff]

                if len(_rate_limit_store[key]) >= limit:
                    return HttpResponse(
                        'Trop de requêtes. Veuillez patienter quelques instants.',
                        status=429,
                        content_type='text/plain; charset=utf-8',
                    )

                _rate_limit_store[key].append(now)

        return self.get_response(request)


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        is_debug = getattr(settings, 'DEBUG', False)

        if is_debug:
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://fonts.gstatic.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: blob:; "
                "connect-src 'self'; "
                "media-src 'self'; "
                "object-src 'none'; "
                "frame-ancestors 'none';"
            )
        else:
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://fonts.gstatic.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: blob: https:; "
                "connect-src 'self'; "
                "media-src 'self'; "
                "object-src 'none'; "
                "upgrade-insecure-requests; "
                "frame-ancestors 'none';"
            )

        response['Content-Security-Policy'] = csp
        response['Permissions-Policy'] = (
            'camera=(), microphone=(), geolocation=(), payment=(), '
            'usb=(), interest-cohort=()'
        )
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        return response
