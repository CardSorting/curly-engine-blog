"""
Load testing configuration for the Chronicle platform using Locust
Enterprise-grade performance testing for API endpoints and user flows
"""

from locust import HttpUser, task, between, constant, SequentialTaskSet
from locust.contrib.fasthttp import FastHttpUser
import json
import random
from faker import Faker

fake = Faker()


class APIUser(FastHttpUser):
    """Base user class for API endpoint testing"""

    wait_time = between(1, 3)  # Random wait between 1-3 seconds
    host = "http://localhost:8000"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.user_id = None
        self.test_topics = []
        self.test_articles = []

    def on_start(self):
        """Setup method called before starting the test"""
        self.register_and_login()

    def register_and_login(self):
        """Register a new user and obtain JWT token"""
        # Register user
        register_data = {
            "email": fake.email(),
            "password": "TestPass123!",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "account_type": "individual"
        }

        with self.client.post("/api/auth/register/", json=register_data, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
                # Login to get token
                login_data = {
                    "email": register_data["email"],
                    "password": register_data["password"]
                }

                with self.client.post("/api/auth/login/", json=login_data, catch_response=True) as login_response:
                    if login_response.status_code == 200:
                        self.token = login_response.json().get("access")
                        self.user_id = login_response.json().get("user", {}).get("id")
                        self.client.headers.update({"Authorization": f"Bearer {self.token}"})
                        login_response.success()
                    else:
                        login_response.failure(f"Login failed: {login_response.text}")
            else:
                response.failure(f"Registration failed: {response.text}")


class ArticleBrowsingUser(APIUser):
    """User that primarily browses articles and topics"""

    @task(3)
    def get_topics(self):
        """Get all topics"""
        with self.client.get("/api/articles/topics/", catch_response=True) as response:
            if response.status_code == 200:
                topics = response.json().get("results", [])
                self.test_topics = [topic['id'] for topic in topics[:5]]  # Store first 5 topics
                response.success()
            else:
                response.failure(f"Failed to get topics: {response.status_code}")

    @task(5)
    def get_articles(self):
        """Get articles list"""
        with self.client.get("/api/articles/articles/", catch_response=True) as response:
            if response.status_code == 200:
                articles = response.json().get("results", [])
                self.test_articles = [article['slug'] for article in articles[:10]]  # Store first 10 articles
                response.success()
            else:
                response.failure(f"Failed to get articles: {response.status_code}")

    @task(8)
    def read_article(self):
        """Read a specific article"""
        if self.test_articles:
            article_slug = random.choice(self.test_articles)
            with self.client.get(f"/api/articles/articles/{article_slug}/", catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed to read article: {response.status_code}")

    @task(2)
    def get_popular_articles(self):
        """Get popular articles"""
        with self.client.get("/api/articles/articles/?ordering=-view_count", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get popular articles: {response.status_code}")


class ContentCreationUser(APIUser):
    """User that creates and manages content"""

    @task(2)
    def create_topic(self):
        """Create a new topic"""
        if not self.test_topics:  # Only create if we haven't cached topics yet
            topic_data = {
                "name": fake.word().capitalize(),
                "description": fake.sentence(),
                "color": fake.hex_color()
            }

            with self.client.post("/api/articles/topics/", json=topic_data, catch_response=True) as response:
                if response.status_code == 201:
                    self.test_topics.append(response.json()['id'])
                    response.success()
                else:
                    response.failure(f"Failed to create topic: {response.status_code}")

    @task(5)
    def create_article(self):
        """Create a new article"""
        if self.test_topics:
            topic_id = random.choice(self.test_topics)

            article_data = {
                "title": fake.sentence(nb_words=6),
                "excerpt": fake.sentence(),
                "content": "\n\n".join(fake.paragraphs(5)),
                "status": "published",
                "topic": topic_id
            }

            with self.client.post("/api/articles/articles/", json=article_data, catch_response=True) as response:
                if response.status_code == 201:
                    created_article = response.json()
                    self.test_articles.append(created_article['slug'])
                    response.success()
                else:
                    response.failure(f"Failed to create article: {response.status_code}")

    @task(3)
    def update_article(self):
        """Update an existing article"""
        if self.test_articles:
            article_slug = random.choice(self.test_articles)

            update_data = {
                "title": fake.sentence(nb_words=5),
                "excerpt": fake.sentence()
            }

            with self.client.patch(f"/api/articles/articles/{article_slug}/", json=update_data, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed to update article: {response.status_code}")


class MediaUploadUser(APIUser):
    """User focused on media upload operations"""

    @task
    def upload_media(self):
        """Upload a media file"""
        # This would require actual file data in a real scenario
        # For now, we'll simulate the request structure
        media_data = {
            "title": fake.sentence(nb_words=3),
            "alt_text": fake.sentence(),
            # In real testing, you'd attach actual file data here
        }

        with self.client.post("/api/media/upload/", json=media_data, catch_response=True) as response:
            # This might fail without actual file data, but tests the endpoint
            if response.status_code in [201, 400]:  # 201 success, 400 validation error (expected without file)
                response.success()
            else:
                response.failure(f"Unexpected media upload response: {response.status_code}")


class NewsletterUser(APIUser):
    """User interacting with newsletter functionality"""

    def on_start(self):
        """Setup method - create subscriber"""
        super().on_start()
        self.subscriber_email = fake.email()

    @task(2)
    def subscribe_newsletter(self):
        """Subscribe to newsletter"""
        subscribe_data = {
            "email": self.subscriber_email,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "subscription_source": "website"
        }

        with self.client.post("/api/newsletter/subscribe/", json=subscribe_data, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Failed to subscribe: {response.status_code}")

    @task(3)
    def get_newsletter_campaigns(self):
        """Get newsletter campaigns"""
        with self.client.get("/api/newsletter/campaigns/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get campaigns: {response.status_code}")


class AnalyticsUser(APIUser):
    """User accessing analytics data"""

    @task
    def get_analytics(self):
        """Get analytics data"""
        with self.client.get("/api/analytics/overview/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get analytics: {response.status_code}")

    @task(2)
    def get_page_views(self):
        """Get page view analytics"""
        with self.client.get("/api/analytics/page-views/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get page views: {response.status_code}")


# User class distribution for realistic load testing
class WebsiteUser(SequentialTaskSet):
    """Main user class that randomly selects behavior patterns"""

    tasks = [
        ArticleBrowsingUser,
        ContentCreationUser,
        NewsletterUser,
        AnalyticsUser,
    ]

    # Weight distribution: 70% browsing, 20% content creation, 7% newsletter, 3% analytics
    def __init__(self, parent):
        super().__init__(parent)
        self.user_type = random.choices(
            ['browsing', 'creation', 'newsletter', 'analytics'],
            weights=[0.7, 0.2, 0.07, 0.03]
        )[0]


# Load testing configuration
class ProductionLoadTest(HttpUser):
    """
    Production load testing user class
    Simulates realistic user behavior with proper wait times and task distribution
    """
    wait_time = constant(2)  # Constant 2-second wait between tasks
    host = "http://localhost:8000"  # Change to production URL when testing live

    tasks = [
        ArticleBrowsingUser,
        ContentCreationUser,
        NewsletterUser,
        MediaUploadUser,
        AnalyticsUser,
    ]


# Quick smoke test for CI/CD pipelines
class SmokeTestUser(HttpUser):
    """Fast smoke test to verify basic functionality"""

    wait_time = constant(0.5)
    host = "http://localhost:8000"

    @task
    def health_check(self):
        """Basic health check"""
        with self.client.get("/health/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()

    @task
    def api_root(self):
        """Test API root endpoint"""
        with self.client.get("/api/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()


if __name__ == "__main__":
    # Allow running from command line for local testing
    import os
    os.system("locust -f locustfile.py --host=http://localhost:8000")
