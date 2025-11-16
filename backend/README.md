# Chronicle Django Backend

REST API backend for the Chronicle blog platform.

## Features

- User authentication with JWT tokens
- Article management with auto-calculated metrics
- Media upload and management
- Topic categorization
- Static pages support
- Email newsletter system (planned)
- Analytics tracking (planned)
- SEO optimization (planned)

## Tech Stack

- Django 5.0.3
- PostgreSQL
- Django REST Framework
- JWT Authentication
- Markdown processing
- AWS S3 support (optional)

## Setup

### Prerequisites

- Python 3.11 or 3.12
- PostgreSQL 15+

### Installation

1. Create virtual environment and activate:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements/development.txt
```

3. Setup environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Authentication
- `POST /api/auth/token/` - Login
- `POST /api/auth/token/refresh/` - Refresh token
- `GET /api/auth/me/` - Current user info

### Articles
- `GET /api/articles/` - List articles
- `POST /api/articles/` - Create article (auth required)
- `GET /api/articles/<slug>/` - Get article
- `PUT /api/articles/<slug>/` - Update article (auth)
- `DELETE /api/articles/<slug>/` - Delete article (auth)

### Topics
- `GET /api/articles/topics/` - List topics
- `GET /api/articles/topics/<slug>/articles/` - Articles by topic

### Media
- `GET /api/media/` - List media files (auth)
- `POST /api/media/upload/` - Upload file (auth)

## Testing

Run tests with pytest:
```bash
pytest
```

With coverage:
```bash
pytest --cov=apps
```

## Development

### Code Quality
```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .
```

### Database
For fresh development environment:
```bash
python manage.py flush  # Clear database
python manage.py createinitialrevisions  # Recreate migrations
```

## Deployment

Use the production requirements:
```bash
pip install -r requirements/production.txt
```

Set production environment variables and collect static files:
```bash
python manage.py collectstatic --noinput
