# Production Setup Guide - World-Class Authentication System

This guide outlines the steps to configure your Django backend for production with the enhanced authentication system.

## 🌐 Environment Variables Configuration

Copy `.env.example` to `.env` and configure the following variables:

### Email Configuration (REQUIRED for email verification)
```bash
# Get your API key from https://resend.com
RESEND_API_KEY=re_your_actual_key_here
FROM_EMAIL=noreply@yoursite.com
```

### Frontend URL Configuration (REQUIRED for email verification links)
```bash
# Your frontend application's URL
FRONTEND_URL=https://yourdomain.com

# Backend URL for admin/documentation
SITE_URL=https://yourdomain.com
```

### Cache Backend (REQUIRED for rate limiting in production)
```bash
# Recommended: Redis for production
CACHE_BACKEND=redis://127.0.0.1:6379/1

# Alternative: Memcached
CACHE_BACKEND=memcached://127.0.0.1:11211/

# Development only (not suitable for production):
CACHE_BACKEND=locmem://
```

### Debug and Security Settings
```bash
# Disable in production!
DEBUG=False

# Your domain in production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 🗄️ Database Setup

For production, use PostgreSQL (already configured):

```bash
DB_NAME=your_prod_db_name
DB_USER=your_prod_db_user
DB_PASSWORD=your_prod_db_password
DB_HOST=your_prod_db_host
DB_PORT=5432
```

## 🔧 Production-Specific Settings

### 1. Install Additional Dependencies

Add these to your `requirements/production.txt`:

```
django-redis==5.4.0  # For Redis cache backend
redis==5.0.1  # For Redis server connection
```

### 2. Redis Installation

For Redis caching (recommended for production):

```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Start Redis
redis-server
```

### 3. Server Configuration

Example gunicorn configuration:

```bash
# install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## 🚀 Deployment Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up PostgreSQL database
- [ ] Configure Redis for caching
- [ ] Set `RESEND_API_KEY` for email sending
- [ ] Set `FRONTEND_URL` for email verification links
- [ ] Test all authentication endpoints
- [ ] Verify email verification flow
- [ ] Test rate limiting functionality
- [ ] Collect static files: `python manage.py collectstatic`

## 🧪 Testing the Enhanced Auth System

### 1. Test Registration with Email Verification

```bash
curl -X POST https://yourdomain.com/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user","password":"Str0ngP@ss123","password_confirm":"Str0ngP@ss123","first_name":"Test","last_name":"User"}'
```

Expected: User created but inactive, verification email sent.

### 2. Test Authentication (Should fail for unverified users)

```bash
curl -X POST https://yourdomain.com/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Str0ngP@ss123"}'
```

Expected: 401 error until email is verified.

### 3. Test Rate Limiting

Try multiple rapid requests to auth endpoints - should get 429 responses.

## 🔒 Security Features Active

Your authentication system now includes:

- ✅ Email verification for all new accounts
- ✅ Strong password requirements (8+ chars, mixed case, numbers, special chars)
- ✅ JWT token authentication with automatic refresh
- ✅ Rate limiting on all auth endpoints (IP-based)
- ✅ Failed login tracking and account lockout
- ✅ Secure token expiration (1 hour access, 7 days refresh)
- ✅ Protected against brute force attacks
- ✅ Professional email templates

## 📊 Monitoring and Maintenance

### Rate Limiting Logs

Monitor your Django logs for rate limiting events:

```bash
tail -f /var/log/django/application.log | grep "rate_limit\|too_many_requests"
```

### Failed Login Monitoring

Track suspicious login attempts:

```bash
# In Django Admin, monitor under "Users" -> Failed Login Attempts
```

## 🆘 Troubleshooting

### Emails Not Sending?
1. Verify `RESEND_API_KEY` is set and valid
2. Check Resend dashboard for email delivery status
3. Ensure `FROM_EMAIL` domain is verified in Resend

### Rate Limiting Not Working?
1. Check Redis is running and accessible
2. Verify `CACHE_BACKEND` URL is correct
3. Ensure Django cache is configured properly

### Email Verification Links Broken?
1. Confirm `FRONTEND_URL` matches your actual frontend domain
2. Check that frontend has route handling for `/auth/verify-email/<token>/`

## 📞 Support

If you encounter issues, check:
1. Django logs: `/var/log/django/application.log`
2. Email service dashboard (Resend)
3. Redis connection: `redis-cli ping`

For technical support, review the codebase or contact the development team.
