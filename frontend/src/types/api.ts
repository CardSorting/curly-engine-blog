// API Response Types
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiError {
  message: string
  status: number
  errors?: Record<string, string[]>
}

// Account Types
export interface Account {
  id: string
  name: string
  slug: string
  description: string
  owner: User
  subscription_plan: SubscriptionPlan | null
  subscription_status: 'trialing' | 'active' | 'past_due' | 'canceled' | 'unpaid'
  current_article_count: number
  current_storage_mb: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface SubscriptionPlan {
  id: string
  name: string
  slug: string
  description: string
  monthly_price: number
  yearly_price: number
  max_users: number
  max_articles: number
  max_storage_mb: number
  features: Record<string, any>
  stripe_price_id_monthly: string
  stripe_price_id_yearly: string
  is_active: boolean
}

// User Types
export interface User {
  id: string
  email: string
  username: string
  bio: string
  avatar: string | null
  is_trialing: boolean
  trial_ends_at: string | null
  email_notifications: boolean
  marketing_emails: boolean
  date_joined: string
  last_login: string | null
}

export interface AccountUser {
  id: string
  account: Account
  user: User
  role: 'admin' | 'editor' | 'author' | 'viewer'
  is_active: boolean
  joined_at: string
}

// Content Types
export interface Topic {
  id: string
  name: string
  slug: string
  description: string
  color: string
}

export interface Article {
  id: string
  title: string
  slug: string
  content: string
  excerpt: string
  author: User
  topic: Topic | null
  hero_image: Media | null
  status: 'draft' | 'published'
  is_published: boolean
  published_at: string | null
  word_count: number
  reading_time: number
  view_count: number
  social_meta?: {
    og_title?: string
    og_description?: string
    og_image?: string
    twitter_card?: string
    twitter_title?: string
    twitter_description?: string
    twitter_image?: string
  }
  created_at: string
  updated_at: string
}

export interface Page {
  id: string
  title: string
  slug: string
  content: string
  meta_description?: string
  is_published: boolean
  created_at: string
  updated_at: string
}

// Media Types
export interface Media {
  id: string
  file: string
  file_name: string
  file_size: number
  mime_type: string
  uploaded_by: User
  alt_text: string
  is_public: boolean
  uploaded_at: string
}

// Newsletter Types
export interface Subscriber {
  id: string
  email: string
  first_name: string
  last_name: string
  subscribed_at: string
  is_active: boolean
  confirmation_token: string | null
}

// Authentication Types
export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  password_confirm: string
  first_name?: string
  last_name?: string
}

export interface TokenResponse {
  access: string
  refresh: string
  user: User
  account?: Account
}

export interface RefreshTokenResponse {
  access: string
}

// API Configuration
export interface RequestConfig {
  account?: string  // Account UUID for multi-tenant requests
}
