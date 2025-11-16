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

// Media Upload Response
export interface MediaUploadResponse {
  file: {
    id: string
    file: string
    file_name: string
    file_size: number
    mime_type: string
    uploaded_by: User
    alt_text: string
    url: string
    name: string
    uploaded_at: string
  }
}

// Analytics Response Types
export interface PageViewAnalytics {
  total: number
  uniqueViews: number
  period: string
  data: Array<{
    date: string
    views: number
    unique_views: number
  }>
}

export interface ArticleAnalytics {
  article_id: string
  views: number
  unique_views: number
  reading_time: number
  bounce_rate: number
  social_shares: number
  comments: number
}

// Topic Response with Results
export interface TopicResponse {
  results: Topic[]
}

// Article Response for editing
export type ArticleResponse = Article

// Page View Response
export type PageViewResponse = Page

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
  features: Record<string, unknown>
  stripe_price_id_monthly: string
  stripe_price_id_yearly: string
  is_active: boolean
}

// Billing and Subscription Types - Industry Standard Features
export interface SubscriptionStatus {
  subscription_status: 'trialing' | 'active' | 'past_due' | 'canceled' | 'unpaid' | 'incomplete'
  subscription_plan: SubscriptionPlan | null
  trial_ends_at: string | null
  subscription_ends_at: string | null
  usage: {
    articles: {
      current: number
      limit: number
      can_create: boolean
    }
    users: {
      current: number
      limit: number
      can_add: boolean
    }
    storage: {
      current: number
      limit: number
    }
  }
  is_trial_active: boolean
  is_subscription_active: boolean
}

export interface BillingInfo {
  subscription_status: string
  subscription_plan: SubscriptionPlan | null
  trial_ends_at: string | null
  subscription_ends_at: string | null
  stripe_customer_id: string | null
  stripe_subscription_id: string | null
  payment_methods: PaymentMethod[]
}

export interface PaymentMethod {
  id: string
  type: string
  card?: {
    brand: string
    last4: string
    exp_month: number
    exp_year: number
  }
  billing_details?: {
    name: string
    email: string
  }
}

export interface Invoice {
  id: string
  number: string
  amount: number
  currency: string
  status: 'draft' | 'open' | 'paid' | 'void' | 'uncollectible'
  created: number
  due_date?: number
  hosted_invoice_url?: string
  invoice_pdf?: string
}

export interface BillingAlert {
  type: 'trial_ending' | 'usage_warning' | 'payment_failed'
  severity: 'warning' | 'error'
  message: string
  action_required: boolean
}

export interface BillingAnalytics {
  current_status: string
  current_plan: string | null
  trial_days_remaining: number | null
  billing_cycle_days_remaining: number | null
  total_invoices: number
  last_payment_date?: string
  next_billing_date?: string
  usage_percentages: {
    users: number
    articles: number
    storage: number
  }
}

export interface ProrationCalculation {
  proration_amount: number
  currency: string
  description: string
}

export interface CouponValidation {
  success: boolean
  error?: string
  coupon?: string
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
  tags: string[]
  featured_image: string
  is_featured: boolean
  allow_comments: boolean
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
