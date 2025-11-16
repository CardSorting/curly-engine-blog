# Curly Engine Blog

A modern multi-tenant blog application built with Django backend, designed for SAAS content management and publishing with tenant-aware architecture.

## Features

- **Multi-Tenant SAAS Architecture**: Account-based content isolation with role-based permissions
- **Django Backend**: Robust REST API with Django and Django REST Framework
- **Modular Architecture**: Organized into separate apps for accounts, analytics, articles, media, and users
- **User Management**: Extended user model with SAAS features and account associations
- **Media Management**: File upload and handling system with S3 integration
- **Database**: SQLite for development, PostgreSQL ready for production
- **Environment Configuration**: Separate settings for development and production
- **Tenant Context**: Automatic tenant filtering and permissions enforcement

## Project Structure

```
blog/
├── backend/
│   ├── apps/
│   │   ├── accounts/      # SAAS account management and tenant handling
│   │   ├── analytics/     # Analytics and tracking
│   │   ├── articles/      # Article management (tenant-aware)
│   │   ├── media/         # Media file handling
│   │   └── users/         # Extended user model with SAAS features
│   ├── config/            # Django configuration
│   ├── media/             # User uploaded files
│   ├── requirements/      # Python dependencies
│   └── manage.py          # Django management script
├── README.md
├── PROGRESS.md            # Development progress tracking
└── blog.md               # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.10+
- pip
- virtualenv (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone git@github.com:CardSorting/curly-engine-blog.git
   cd curly-engine-blog
   ```

2. **Create and activate virtual environment**
   ```bash
   cd backend
   python -m venv venv
   
   # On macOS/Linux
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Environment setup**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your configuration
   # Add SECRET_KEY, DEBUG settings, database credentials, etc.
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://127.0.0.1:8000/`

## Configuration

### Environment Variables

Key environment variables to configure in `.env`:

```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (if using PostgreSQL/MySQL in production)
DATABASE_URL=sqlite:///db.sqlite3  # Default for development

# Media Files
MEDIA_ROOT=backend/media/uploads
MEDIA_URL=/media/
```

### Production Deployment

For production deployment:

1. Install production dependencies:
   ```bash
   pip install -r requirements/production.txt
   ```

2. Set environment variables:
   ```bash
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

3. Use a production database (PostgreSQL recommended)

4. Configure static files serving
5. Set up proper security headers
6. Configure domain and SSL

## Apps Overview

### Accounts App
Manages SAAS tenant accounts, subscriptions, and multi-tenancy features. Handles account isolation, user roles, and tenant context.

### Users App
Extended user model with SAAS features including default account associations, trial management, and role-based permissions.

### Articles App
Manages blog posts, articles, and content creation with tenant-aware filtering and permissions.

### Analytics App
Handles tracking, statistics, and analytics data with tenant isolation.

### Media App
Manages file uploads, images, and media assets with S3 integration.

## SAAS Features

### Multi-Tenancy
- Account-based data isolation
- Tenant-aware models (Article, Topic, Page)
- Automatic tenant filtering in all API endpoints
- Role-based permissions per account

### User Roles
- **Account Admin**: Full account management
- **Account Editor**: Can create and edit content
- **Account Viewer**: Read-only access to content

### Subscription Management
- Trial periods for new accounts
- Subscription status tracking
- Plan-based feature access

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
This project follows PEP 8 Python style guidelines.

### Adding New Apps
```bash
python manage.py startapp new_app_name
# Move the app to backend/apps/
# Add to INSTALLED_APPS in settings
# For tenant-aware apps, add account ForeignKey to models
```

### Database Management
```bash
# Create migrations for tenant-aware changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (development only)
python manage.py reset_database
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please open an issue in the GitHub repository.

---

**Built with Django** ❤️
