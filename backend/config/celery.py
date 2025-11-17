"""
Celery configuration for background task processing
Enterprise-grade task queue setup with Redis as broker and result backend
"""

import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
from django.utils import timezone

# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the Celery app instance
app = Celery('chronicle')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Newsletter delivery tasks
    'process-pending-newsletters': {
        'task': 'apps.newsletter.tasks.process_pending_newsletters',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },

    # Email campaign analytics updates
    'update-email-analytics': {
        'task': 'apps.newsletter.tasks.update_email_analytics',
        'schedule': crontab(hour='*/2'),  # Every 2 hours
    },

    # Content performance calculations
    'calculate-content-performance': {
        'task': 'apps.analytics.tasks.calculate_content_performance',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
    },

    # Clean up expired sessions and temporary data
    'cleanup-expired-data': {
        'task': 'apps.core.tasks.cleanup_expired_data',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },

    # Generate sitemap and SEO updates
    'update-sitemap-seo': {
        'task': 'apps.seo.tasks.update_sitemap_and_seo',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },

    # Backup critical data
    'perform-database-backup': {
        'task': 'apps.core.tasks.perform_database_backup',
        'schedule': crontab(hour=4, minute=0),  # Daily at 4 AM
    },

    # Process media optimization queue
    'optimize-media-files': {
        'task': 'apps.media.tasks.optimize_media_files',
        'schedule': crontab(hour='*/4'),  # Every 4 hours
    },

    # Update subscription statuses and billing
    'update-subscription-statuses': {
        'task': 'apps.accounts.tasks.update_subscription_statuses',
        'schedule': crontab(hour='*/12'),  # Every 12 hours
    },
}

# Configure Celery for enterprise-scale deployment
app.conf.update(
    # Task routing for worker scaling
    task_routes = {
        'apps.newsletter.tasks.*': {'queue': 'newsletter'},
        'apps.analytics.tasks.*': {'queue': 'analytics'},
        'apps.media.tasks.*': {'queue': 'media'},
        'apps.accounts.tasks.*': {'queue': 'billing'},
        'apps.seo.tasks.*': {'queue': 'seo'},
        'apps.core.tasks.*': {'queue': 'maintenance'},
    },

    # Worker configuration
    worker_prefetch_multiplier = 1,  # One task per worker process
    worker_max_tasks_per_child = 1000,  # Restart worker after 1000 tasks
    worker_disable_rate_limits = False,

    # Result backend configuration
    result_expires = 3600,  # Results expire after 1 hour
    result_compression = 'gzip',

    # Task serialization
    task_serializer = 'json',
    accept_content = ['json'],
    result_serializer = 'json',
    timezone = 'UTC',
    enable_utc = True,

    # Error handling and retries
    task_default_retry_delay = 60,  # 1 minute delay between retries
    task_max_retries = 3,
    task_acks_late = True,  # Tasks acknowledged after completion
    task_reject_on_worker_lost = True,

    # Monitoring and logging
    worker_send_task_events = True,
    task_send_sent_event = True,
    task_track_started = True,

    # Rate limiting (additional layer beyond Django middleware)
    worker_disable_rate_limits = False,
)

# Celery Beat configuration
app.conf.beat_schedule_filename = os.path.join(settings.BASE_DIR, 'celerybeat-schedule.db')
app.conf.beat_max_loop_interval = 300  # 5 minutes max loop interval


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f'Request: {self.request!r}')


# Utility function to run tasks synchronously in development
def run_task_synchronously(task_name, *args, **kwargs):
    """
    Run a Celery task synchronously (for development/testing)
    Returns the task result directly instead of AsyncResult
    """
    try:
        task = app.tasks[task_name]
        return task.apply(args=args, kwargs=kwargs, throw=True)
    except Exception as e:
        # Log the error and re-raise for debugging
        print(f"Error running task {task_name}: {e}")
        raise


# Health check task for monitoring
@app.task
def health_check():
    """Basic health check task for monitoring Celery"""
    from django.db import connection
    from django.core.cache import cache

    # Test database connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        db_status = cursor.fetchone()[0] == 1

    # Test cache connection
    cache.set('celery_health_check', 'ok', 30)
    cache_status = cache.get('celery_health_check') == 'ok'

    return {
        'status': 'healthy' if db_status and cache_status else 'unhealthy',
        'database': db_status,
        'cache': cache_status,
        'timestamp': str(timezone.now())
    }
