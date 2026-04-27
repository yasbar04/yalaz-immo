from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    Returns 200 if all systems are operational.
    """
    health_status = {}
    status_code = 200

    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['database'] = 'ok'
    except Exception as e:
        health_status['database'] = f'error: {str(e)}'
        status_code = 503
        logger.error(f"Database health check failed: {e}")

    # Check cache (Redis)
    try:
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        health_status['cache'] = 'ok'
    except Exception as e:
        health_status['cache'] = f'error: {str(e)}'
        logger.warning(f"Cache health check failed: {e}")

    # Basic status
    health_status['status'] = 'healthy' if status_code == 200 else 'degraded'

    return JsonResponse(
        health_status,
        status=status_code,
        content_type='application/json'
    )
