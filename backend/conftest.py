import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.core.management import execute_from_command_line
import factory
from faker import Faker
from rest_framework.test import APIClient
from apps.articles.models import Article, Topic, Page
from apps.media.models import MediaItem
from apps.newsletter.models import Subscriber, Newsletter

User = get_user_model()
fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users"""
    class Meta:
        model = User

    email = factory.LazyAttribute(lambda x: fake.email())
    first_name = factory.LazyAttribute(lambda x: fake.first_name())
    last_name = factory.LazyAttribute(lambda x: fake.last_name())
    is_active = True
    is_staff = False

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.set_password(extracted)
        else:
            self.set_password('testpass123')
        self.save()


class TopicFactory(factory.django.DjangoModelFactory):
    """Factory for creating test topics"""
    class Meta:
        model = Topic

    name = factory.LazyAttribute(lambda x: fake.word().capitalize())
    slug = factory.LazyAttribute(lambda obj: fake.slug(obj.name.lower()))
    description = factory.LazyAttribute(lambda x: fake.sentence())
    color = factory.LazyAttribute(lambda x: fake.hex_color())


class ArticleFactory(factory.django.DjangoModelFactory):
    """Factory for creating test articles"""
    class Meta:
        model = Article

    title = factory.LazyAttribute(lambda x: fake.sentence(nb_words=6)[:-1])
    slug = factory.LazyAttribute(lambda obj: fake.slug(obj.title.lower()))
    excerpt = factory.LazyAttribute(lambda x: fake.sentence())
    content = factory.LazyAttribute(lambda x: '\n\n'.join(fake.paragraphs(5)))
    status = 'published'
    author = factory.SubFactory(UserFactory)
    topic = factory.SubFactory(TopicFactory)

    @factory.post_generation
    def published_at(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.published_at = extracted
        elif self.status == 'published':
            self.published_at = fake.date_time_this_year()
        self.save()


class SubscriberFactory(factory.django.DjangoModelFactory):
    """Factory for creating test subscribers"""
    class Meta:
        model = Subscriber

    email = factory.LazyAttribute(lambda x: fake.email())
    first_name = factory.LazyAttribute(lambda x: fake.first_name())
    last_name = factory.LazyAttribute(lambda x: fake.last_name())
    is_active = True
    is_confirmed = True

    # Add realistic subscription preferences for A/B testing
    subscription_source = factory.LazyAttribute(lambda x: fake.random_element(['website', 'newsletter', 'referral', 'social']))
    tags = factory.LazyAttribute(lambda x: [fake.word() for _ in range(fake.random_int(0, 3))])


class MediaItemFactory(factory.django.DjangoModelFactory):
    """Factory for creating test media items - essential for rich content testing"""
    class Meta:
        model = MediaItem

    title = factory.LazyAttribute(lambda x: fake.sentence(nb_words=4)[:-1])
    file = factory.LazyAttribute(lambda x: f"media/test/{fake.file_name(extension='jpg')}")
    file_type = factory.LazyAttribute(lambda x: fake.random_element(['image', 'video', 'document']))
    mime_type = factory.LazyAttribute(lambda x: fake.random_element(['image/jpeg', 'video/mp4', 'application/pdf']))
    file_size = factory.LazyAttribute(lambda x: fake.random_int(1024, 1024*1024*10))  # 1KB to 10MB
    uploaded_by = factory.SubFactory(UserFactory)


@pytest.fixture
def media_item():
    """Create a test media item"""
    return MediaItemFactory()


@pytest.fixture
def newsletter():
    """Create a test newsletter"""
    return Newsletter.objects.create(
        subject=fake.sentence(nb_words=6)[:-1],
        content='\n\n'.join(fake.paragraphs(3)),
        status='draft',
        sent_at=None
    )


# Test data generators for load testing scenarios
@pytest.fixture
def bulk_users():
    """Create a bulk set of users for performance testing"""
    return UserFactory.create_batch(50)


@pytest.fixture
def bulk_articles(bulk_users, topic):
    """Create a bulk set of articles for performance testing"""
    return ArticleFactory.create_batch(100, topic=topic, author=factory.Iterator(bulk_users))


@pytest.fixture
def bulk_subscribers():
    """Create a bulk set of subscribers for email testing"""
    return SubscriberFactory.create_batch(200)


@pytest.fixture
def user():
    """Create a test user"""
    return UserFactory()


@pytest.fixture
def admin_user():
    """Create an admin test user"""
    return UserFactory(is_staff=True, is_superuser=True)


@pytest.fixture
def topic():
    """Create a test topic"""
    return TopicFactory()


@pytest.fixture
def article(topic):
    """Create a test article"""
    return ArticleFactory(topic=topic)


@pytest.fixture
def subscriber():
    """Create a test subscriber"""
    return SubscriberFactory()


@pytest.fixture
def api_client():
    """Create a REST API client"""
    return APIClient()


@pytest.fixture
def authenticated_client(user):
    """Create an authenticated REST API client"""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_client(admin_user):
    """Create an admin REST API client"""
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture(scope='session', autouse=True)
def django_db_setup(django_db_setup, django_db_blocker):
    """Run database migrations before tests"""
    with django_db_blocker.unblock():
        # Make sure we're using a test database
        from django.conf import settings
        if 'test' not in settings.DATABASES['default']['NAME']:
            raise Exception("Running tests on non-test database!")

        # Run migrations
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=0'])
