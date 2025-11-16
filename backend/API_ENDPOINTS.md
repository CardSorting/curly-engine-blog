# API Endpoints Summary

## Base URL
`http://localhost:8000`

## Authentication
All endpoints except article listing and page listing require authentication.

### Get Token
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "adminpass123"}'
```

### Use Token
Add header: `Authorization: Bearer <access_token>`

## Endpoints

### Articles
- **List**: `GET /api/` - Lists all published articles (no auth required)
- **Detail**: `GET /api/detail/<slug>/` - Get single article by slug
- **Create**: `POST /api/` - Create new article (auth required)
- **Update**: `PUT/PATCH /api/detail/<slug>/` - Update article (auth required)
- **Delete**: `DELETE /api/detail/<slug>/` - Delete article (auth required)
- **Publish**: `POST /api/detail/<slug>/publish/` - Publish article (auth required)

### Topics
- **List**: `GET /api/topics/` - List all topics
- **Detail**: `GET /api/topics/<slug>/` - Get topic details
- **Articles**: `GET /api/topics/<slug>/articles/` - List articles in topic

### Pages
- **List**: `GET /api/pages/` - List all pages (no auth required)
- **Detail**: `GET /api/pages/<slug>/` - Get page by slug (no auth required)

### Media
- **List**: `GET /api/media/` - List media files (auth required)
- **Upload**: `POST /api/media/upload/` - Upload media file (auth required)
- **Detail**: `GET /api/media/<uuid>/` - Get media details (auth required)
- **Delete**: `DELETE /api/media/<uuid>/` - Delete media file (auth required)
- **Stats**: `GET /api/media/stats/` - Get media statistics (auth required)

### Users
- **Register**: `POST /api/register/` - Register new user
- **Profile**: `GET/PUT/PATCH /api/profile/` - Get/update user profile (auth required)
- **Current User**: `GET /api/auth/me/` - Get current user info (auth required)
- **Refresh Token**: `POST /api/auth/token/refresh/` - Refresh access token

### Newsletter
- **Subscribe**: `POST /api/newsletter/subscribers/subscribe/` - Subscribe to newsletter
- **Unsubscribe**: `POST /api/newsletter/subscribers/unsubscribe/` - Unsubscribe
- **Confirm**: `POST /api/newsletter/subscribers/confirm/` - Confirm subscription
- **List**: `GET /api/newsletter/subscribers/` - List subscribers (auth required)

## Testing

### Test all endpoints
```bash
# Articles
curl http://localhost:8000/api/
curl http://localhost:8000/api/detail/getting-started-with-django-rest-framework/

# Topics
curl http://localhost:8000/api/topics/
curl http://localhost:8000/api/topics/web-development/

# Pages
curl http://localhost:8000/api/pages/
curl http://localhost:8000/api/pages/about-us/

# Media (requires auth)
TOKEN="<your_access_token>"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/media/
```
