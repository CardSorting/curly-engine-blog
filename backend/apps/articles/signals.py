from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Article
import markdown


@receiver(post_save, sender=Article)
def clear_cache_on_article_save(sender, instance, **kwargs):
    """Clear relevant cache entries when an article is saved"""
    # Clear specific cache entries
    cache.delete('sitemap_articles')
    cache.delete('rss_feed')
    cache.delete('featured_articles')

    if instance.topic:
        cache.delete(f'topic_articles_{instance.topic.slug}')


@receiver(post_save, sender=Article)
def generate_html_content(sender, instance, **kwargs):
    """
    Convert markdown content to HTML and store in cache
    """
    if instance.content:
        html_content = markdown.markdown(instance.content)
        cache_key = f'article_html_{instance.id}'
        cache.set(cache_key, html_content, 3600)  # Cache for 1 hour
