# Curly Engine Blog

A modern blog application built with Django backend, designed for content management and publishing.

## Features

- **Django Backend**: Robust REST API with Django and Django REST Framework
- **Modular Architecture**: Organized into separate apps for analytics, articles, and media
- **Media Management**: File upload and handling system
- **Database**: SQLite for development (easily configurable for production)
- **Environment Configuration**: Separate settings for development and production

## Project Structure

```
blog/
├── backend/
│   ├── apps/
│   │   ├── analytics/     # Analytics and tracking
│   │   ├── articles/      # Article management
│   │   └── media/         # Media file handling
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

### Articles App
Manages blog posts, articles, and content creation.

### Analytics App
Handles tracking, statistics, and analytics data.

### Media App
Manages file uploads, images, and media assets.

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
