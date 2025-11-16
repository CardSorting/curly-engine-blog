# Frontend Integration Guide

This guide provides instructions and examples for integrating frontend applications with the Chronicle Blog API.

## 🚀 Quick Start

### Base URL
```
Development: http://localhost:8000/api/
Production: https://your-domain.com/api/
```

### Authentication
The API uses JWT (JSON Web Tokens) for authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

## 🔐 Authentication Endpoints

### Register a New User

```javascript
const response = await fetch('/api/auth/register/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'securepassword123',
    first_name: 'John',
    last_name: 'Doe'
  })
});

const data = await response.json();
// Returns: { access: '...', refresh: '...' }
```

### Login

```javascript
const response = await fetch('/api/auth/token/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'securepassword123'
  })
});

const data = await response.json();
// Returns: { access: '...', refresh: '...' }
```

### Refresh Token

```javascript
const response = await fetch('/api/auth/token/refresh/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    refresh: 'your-refresh-token'
  })
});

const data = await response.json();
// Returns: { access: '...' }
```

### Get Current User

```javascript
const response = await fetch('/api/auth/me/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const user = await response.json();
// Returns: { id: '...', email: '...', first_name: '...', last_name: '...', bio: '...' }
```

## 📝 Articles Endpoints

### List Articles

```javascript
const response = await fetch('/api/?page=1&page_size=10', {
  headers: {
    'Authorization': `Bearer ${accessToken}` // Optional for public articles
  }
});

const data = await response.json();
// Returns: { count: 25, next: '...', previous: null, results: [...] }
```

### Get Article by Slug

```javascript
const response = await fetch('/api/detail/my-article-slug/');
const article = await response.json();
// Returns: { id: '...', title: '...', content: '...', author: {...}, topic: {...}, ... }
```

### Create Article (Authenticated Authors Only)

```javascript
const response = await fetch('/api/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: 'My Article Title',
    excerpt: 'Brief description of the article',
    content: '# Markdown Content\n\nThis is the full article content.',
    status: 'draft', // or 'published'
    topic: 'topic-uuid' // optional
  })
});

const article = await response.json();
```

### Update Article (Author or Admin Only)

```javascript
const response = await fetch(`/api/detail/${articleSlug}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: 'Updated Title',
    content: 'Updated content'
  })
});

const updatedArticle = await response.json();
```

### Publish Article (Admin Only)

```javascript
const response = await fetch(`/api/detail/${articleSlug}/publish/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  }
});

const publishedArticle = await response.json();
```

## 🏷️ Topics Endpoints

### List Topics

```javascript
const response = await fetch('/api/topics/');
const topics = await response.json();
// Returns: [{ id: '...', name: '...', slug: '...', description: '...', color: '...' }, ...]
```

### Get Topic Articles

```javascript
const response = await fetch('/api/topics/technology/articles/');
const data = await response.json();
// Returns: { count: 10, next: '...', previous: null, results: [...] }
```

## 📄 Pages Endpoints

### List Pages

```javascript
const response = await fetch('/api/pages/');
const pages = await response.json();
// Returns: [{ id: '...', title: '...', slug: '...', content: '...' }, ...]
```

### Get Page by Slug

```javascript
const response = await fetch('/api/pages/about/');
const page = await response.json();
// Returns: { id: '...', title: '...', slug: '...', content: '...' }
```

## 📎 Media Upload Endpoints

### Upload File (Authenticated Users Only)

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]); // File object
formData.append('title', 'My Image');
formData.append('alt_text', 'Alt text for accessibility');
formData.append('caption', 'Optional caption');

const response = await fetch('/api/media/upload/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
  },
  body: formData
});

const mediaItem = await response.json();
// Returns: { id: '...', file: '/media/uploads/...', title: '...', ... }
```

### List User's Media Files

```javascript
const response = await fetch('/api/media/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const mediaList = await response.json();
// Returns: { count: 5, next: null, previous: null, results: [...] }
```

### Delete Media File (Owner Only)

```javascript
const response = await fetch(`/api/media/${mediaId}/`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
// Returns: 204 No Content on success
```

## 📊 Analytics Endpoints

### Track Page View

```javascript
const response = await fetch('/api/analytics/track/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    content_type: 'article', // or 'page', 'topic', 'home'
    object_id: 'article-uuid', // optional
    url: window.location.pathname,
    session_id: 'unique-session-id',
    referrer: document.referrer,
    time_on_page: 120 // seconds, optional
  })
});

// Returns: { status: 'tracked', id: '...' }
```

### Get Analytics Dashboard (Admin Only)

```javascript
const response = await fetch('/api/analytics/dashboard/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const analytics = await response.json();
// Returns: { overview: {...}, content_breakdown: [...], top_articles: [...], ... }
```

## 📧 Newsletter Endpoints

### Subscribe to Newsletter

```javascript
const response = await fetch('/api/newsletter/subscribe/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'subscriber@example.com',
    first_name: 'John',
    last_name: 'Doe'
  })
});

const result = await response.json();
// Returns: { message: 'Subscription successful. Please check your email to confirm.' }
```

### Unsubscribe from Newsletter

```javascript
const response = await fetch('/api/newsletter/unsubscribe/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    token: 'unsubscribe-token-from-email'
  })
});

const result = await response.json();
// Returns: { message: 'Successfully unsubscribed.' }
```

## 🏷️ SEO Endpoints

### Get Meta Tags for URL

```javascript
const response = await fetch('/api/seo/meta-tags/?url=/articles/my-article/');
const metaTags = await response.json();
// Returns: { title: '...', description: '...', keywords: '...', ... }
```

### Get Structured Data (JSON-LD)

```javascript
const response = await fetch('/api/seo/schema/?url=/articles/my-article/');
const schema = await response.json();
// Returns: { "@context": "https://schema.org", "@type": "Article", ... }
```

## 🔧 JavaScript SDK Example

### API Client Class

```javascript
class ChronicleAPI {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('access_token');
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (this.token) {
      config.headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, config);

    if (response.status === 401 && this.token) {
      // Token might be expired, try to refresh
      await this.refreshToken();
      return this.request(endpoint, options);
    }

    return response.json();
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken })
      });

      if (response.ok) {
        const data = await response.json();
        this.setToken(data.access);
        return true;
      }
    } catch (error) {
      console.error('Failed to refresh token:', error);
    }

    return false;
  }

  // Authentication methods
  async login(email, password) {
    const data = await this.request('/auth/token/', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });

    if (data.access) {
      this.setToken(data.access);
      localStorage.setItem('refresh_token', data.refresh);
    }

    return data;
  }

  async register(userData) {
    return this.request('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  }

  async getCurrentUser() {
    return this.request('/auth/me/');
  }

  // Articles methods
  async getArticles(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/?${queryString}` : '/';
    return this.request(endpoint);
  }

  async getArticle(slug) {
    return this.request(`/detail/${slug}/`);
  }

  async createArticle(articleData) {
    return this.request('/', {
      method: 'POST',
      body: JSON.stringify(articleData)
    });
  }

  async updateArticle(slug, articleData) {
    return this.request(`/detail/${slug}/`, {
      method: 'PATCH',
      body: JSON.stringify(articleData)
    });
  }

  // Media methods
  async uploadFile(file, metadata = {}) {
    const formData = new FormData();
    formData.append('file', file);
    Object.keys(metadata).forEach(key => {
      formData.append(key, metadata[key]);
    });

    return this.request('/media/upload/', {
      method: 'POST',
      headers: {}, // Don't set Content-Type, let browser set it
      body: formData
    });
  }

  async getMedia() {
    return this.request('/media/');
  }

  // Newsletter methods
  async subscribe(email, firstName, lastName) {
    return this.request('/newsletter/subscribe/', {
      method: 'POST',
      body: JSON.stringify({
        email,
        first_name: firstName,
        last_name: lastName
      })
    });
  }

  // Analytics tracking
  async trackPageView(pageData) {
    return this.request('/analytics/track/', {
      method: 'POST',
      body: JSON.stringify(pageData)
    });
  }
}

// Usage example
const api = new ChronicleAPI();

// Login
await api.login('user@example.com', 'password');

// Get articles
const articles = await api.getArticles({ page: 1, page_size: 10 });

// Upload file
const fileInput = document.getElementById('file-input');
if (fileInput.files[0]) {
  const result = await api.uploadFile(fileInput.files[0], {
    title: 'My uploaded file',
    alt_text: 'Description of the file'
  });
  console.log('Upload successful:', result);
}
```

## ⚠️ Error Handling

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **204 No Content**: Request successful, no content returned (common for DELETE)
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Error Response Format

```json
{
  "detail": "Authentication credentials were not provided.",
  "code": "not_authenticated"
}
```

Or for validation errors:

```json
{
  "email": ["This field is required."],
  "password": ["Password must be at least 8 characters long."]
}
```

## 🚀 Vue.js Integration Example

```javascript
// composables/useAPI.js
import { ref, computed } from 'vue'

const API_BASE_URL = 'http://localhost:8000/api'
const accessToken = ref(localStorage.getItem('access_token') || '')

export function useAPI() {
  const isAuthenticated = computed(() => !!accessToken.value)

  const apiRequest = async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    if (accessToken.value) {
      config.headers.Authorization = `Bearer ${accessToken.value}`
    }

    try {
      const response = await fetch(url, config)

      if (response.status === 401 && accessToken.value) {
        // Try to refresh token
        const refreshed = await refreshToken()
        if (refreshed) {
          // Retry request with new token
          config.headers.Authorization = `Bearer ${accessToken.value}`
          return apiRequest(endpoint, { ...options, headers: config.headers })
        }
      }

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'API request failed')
      }

      return response.json()
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error)
      throw error
    }
  }

  const refreshToken = async () => {
    const refresh = localStorage.getItem('refresh_token')
    if (!refresh) return false

    try {
      const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh })
      })

      if (response.ok) {
        const data = await response.json()
        setToken(data.access)
        return true
      }
    } catch (error) {
      console.error('Token refresh failed:', error)
      logout()
    }
    return false
  }

  const setToken = (token) => {
    accessToken.value = token
    localStorage.setItem('access_token', token)
  }

  const logout = () => {
    accessToken.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  const login = async (email, password) => {
    const data = await apiRequest('/auth/token/', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    })

    setToken(data.access)
    localStorage.setItem('refresh_token', data.refresh)
    return data
  }

  const register = async (userData) => {
    const data = await apiRequest('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(userData)
    })

    if (data.access) {
      setToken(data.access)
      localStorage.setItem('refresh_token', data.refresh)
    }

    return data
  }

  return {
    isAuthenticated,
    login,
    register,
    logout,
    apiRequest
  }
}
```

## 🔗 Resources

- **[API Documentation](/api/schema/swagger-ui/)** - Interactive Swagger UI
- **[API Schema](/api/schema/)** - OpenAPI JSON schema
- **[Redoc Documentation](/api/schema/redoc/)** - Alternative documentation UI

## 🆘 Troubleshooting

### CORS Issues
If you encounter CORS errors in development, ensure your frontend is running on an allowed origin (configured in `CORS_ALLOWED_ORIGINS` setting).

### Token Expiration
The API returns 401 status for expired tokens. Implement automatic token refresh in your client application.

### File Upload Issues
- Ensure you're using `FormData` for file uploads
- Don't set `Content-Type` header manually for multipart/form-data requests
- Maximum file size limits may apply (default: 2.5MB)

### Rate Limiting
The API may implement rate limiting for certain endpoints. Implement exponential backoff for failed requests.
