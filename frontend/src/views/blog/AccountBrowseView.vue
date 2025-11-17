<template>
  <div class="min-h-screen bg-white">
    <!-- TechCrunch-style Minimal Header -->
    <header class="bg-white border-b border-gray-100 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-8">
            <!-- TechCrunch-style Logo -->
            <router-link to="/" class="text-2xl font-bold text-red-500 hover:text-red-600 transition-colors">
              Chronicle
            </router-link>

            <!-- TechCrunch-style Navigation -->
            <nav class="hidden lg:flex items-center">
              <div class="flex items-center space-x-1">
                <span class="text-xs font-medium text-gray-400 uppercase tracking-wider">Latest</span>
                <div class="w-px h-4 bg-gray-300 mx-3"></div>
              </div>
              <div class="flex items-center space-x-1">
                <button
                  v-for="category in categories.slice(0, 5)"
                  :key="category.slug"
                  @click="filterByCategory(category.slug)"
                  class="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium transition-colors relative rounded-sm hover:bg-gray-50"
                  :class="{ 'text-red-500': selectedCategory === category.slug }"
                >
                  {{ category.name }}
                </button>
              </div>
            </nav>
          </div>

          <div class="flex items-center space-x-3">
            <!-- Search Icon -->
            <button
              @click="showSearch = !showSearch"
              class="text-gray-400 hover:text-gray-600 p-2 rounded-full hover:bg-gray-50 transition-colors"
            >
              <MagnifyingGlassIcon class="h-5 w-5" />
            </button>

            <!-- Theme Toggle -->
            <ThemeToggle />

            <!-- Minimal Auth Links -->
            <div class="hidden md:flex items-center space-x-4 ml-4 pl-4 border-l border-gray-200">
              <router-link
                to="/login"
                class="text-gray-600 hover:text-gray-900 text-sm font-medium transition-colors"
              >
                Sign In
              </router-link>
              <router-link
                to="/register"
                class="bg-red-500 text-white px-4 py-2 text-sm font-medium rounded-full hover:bg-red-600 transition-colors"
              >
                Start Writing
              </router-link>
            </div>
          </div>
        </div>

        <!-- Mobile Navigation -->
        <div v-if="showMobileNav" class="md:hidden border-t border-gray-200 py-4">
          <nav class="flex flex-wrap gap-2">
            <button
              v-for="category in categories"
              :key="category.slug"
              @click="filterByCategory(category.slug)"
              class="text-sm text-gray-600 hover:text-gray-900 px-3 py-1 rounded-md hover:bg-gray-100 transition-colors"
              :class="{ 'bg-blue-50 text-blue-600': selectedCategory === category.slug }"
            >
              {{ category.name }}
            </button>
          </nav>
        </div>
      </div>

      <!-- Search Overlay -->
      <div
        v-if="showSearch"
        class="absolute top-full left-0 w-full bg-white border-b border-gray-200 shadow-lg z-40"
      >
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div class="flex items-center space-x-4">
            <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search articles..."
              class="flex-1 text-lg border-0 focus:outline-none focus:ring-0"
              @keyup.enter="performSearch"
            >
            <button
              @click="showSearch = false"
              class="text-gray-400 hover:text-gray-600 p-1"
            >
              <XMarkIcon class="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- World-Class Featured Article with Social Proof -->
        <article
          v-if="featuredArticles[0]"
          class="mb-20 group cursor-pointer relative"
          @click="navigateToArticle(featuredArticles[0])"
        >
          <!-- Subtle background gradient -->
          <div class="absolute inset-0 bg-gradient-to-br from-red-50/50 via-transparent to-transparent pointer-events-none"></div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center relative">
            <!-- Enhanced Content Section -->
            <div class="order-2 lg:order-1 space-y-8">
              <!-- Credibility Badge -->
              <div class="flex items-center space-x-3">
                <div v-if="featuredArticles[0].topic" class="inline-block">
                  <span
                    class="px-4 py-2 text-xs font-bold uppercase tracking-wide rounded-md text-white shadow-sm"
                    :style="{ backgroundColor: featuredArticles[0].topic.color }"
                  >
                    {{ featuredArticles[0].topic.name }}
                  </span>
                </div>
                <div class="flex items-center text-xs text-gray-500 font-medium">
                  <span>Featured Article</span>
                  <div class="w-1 h-1 bg-gray-400 rounded-full mx-2"></div>
                  <span>{{ formatDate(featuredArticles[0].published_at!) }}</span>
                </div>
              </div>

              <!-- Premium Typography -->
              <h1 class="text-5xl lg:text-6xl xl:text-7xl font-black text-gray-900 group-hover:text-red-500 transition-all duration-300 leading-[0.9] tracking-tight">
                {{ featuredArticles[0].title }}
              </h1>

              <!-- Enhanced Excerpt -->
              <p class="text-xl lg:text-2xl text-gray-600 leading-relaxed max-w-xl font-medium">
                {{ featuredArticles[0].excerpt }}
              </p>

              <!-- Professional Author Byline -->
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                  <div class="relative">
                    <div class="w-14 h-14 bg-gradient-to-br from-red-400 to-red-600 rounded-full flex items-center justify-center shadow-lg">
                      <span class="text-lg font-black text-white uppercase">
                        {{ featuredArticles[0].author.username.charAt(0) }}
                      </span>
                    </div>
                    <!-- Verified badge -->
                    <div class="absolute -bottom-1 -right-1 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center border-2 border-white">
                      <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                      </svg>
                    </div>
                  </div>
                  <div class="space-y-1">
                    <div class="font-bold text-gray-900 text-lg">{{ featuredArticles[0].author.username }}</div>
                    <div class="text-sm text-gray-600">Senior Technology Correspondent</div>
                    <div class="flex items-center space-x-3 text-xs text-gray-500">
                      <span>✨ {{ featuredArticles[0].reading_time }} min read</span>
                      <span>👁️ {{ formatViewCount(featuredArticles[0].view_count) }} views</span>
                    </div>
                  </div>
                </div>

                <!-- Social Share Preview -->
                <div class="hidden lg:flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <span class="text-xs text-gray-500 uppercase tracking-wide font-semibold">Share</span>
                  <button class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center hover:bg-blue-700 transition-colors" @click.stop="shareOnTwitter(featuredArticles[0])">
                    <span class="sr-only">Share on Twitter</span>
                    <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                    </svg>
                  </button>
                  <button class="w-8 h-8 bg-blue-700 rounded-full flex items-center justify-center hover:bg-blue-800 transition-colors" @click.stop="shareOnLinkedIn(featuredArticles[0])">
                    <span class="sr-only">Share on LinkedIn</span>
                    <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Enhanced Hero Image -->
            <div class="order-1 lg:order-2 relative">
              <div class="aspect-[4/3] overflow-hidden rounded-xl shadow-2xl">
                <img
                  v-if="featuredArticles[0].hero_image"
                  :src="featuredArticles[0].hero_image.file"
                  :alt="featuredArticles[0].hero_image.alt_text || featuredArticles[0].title"
                  class="w-full h-full object-cover group-hover:scale-105 transition-all duration-700"
                  loading="eager"
                />
                <div v-else class="w-full h-full bg-gradient-to-br from-red-100 to-red-200 flex items-center justify-center">
                  <NewspaperIcon class="h-32 w-32 text-red-400" />
                </div>

                <!-- Enhanced Gradient Overlay -->
                <div class="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

                <!-- Article Stats Overlay -->
                <div class="absolute bottom-4 left-4 right-4 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
                  <div class="bg-white/95 backdrop-blur-sm rounded-lg px-4 py-3">
                    <div class="flex items-center justify-between text-sm">
                      <div class="flex items-center space-x-4 text-gray-700">
                        <span class="flex items-center space-x-1">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                          </svg>
                          <span>{{ formatViewCount(featuredArticles[0].view_count) }}</span>
                        </span>
                        <span class="flex items-center space-x-1">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                          </svg>
                          <span>{{ featuredArticles[0].reading_time }} min</span>
                        </span>
                      </div>
                      <span class="text-red-600 font-semibold">{{ formatDate(featuredArticles[0].published_at!) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </article>

        <!-- Secondary Articles Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <article
            v-for="article in featuredArticles.slice(1)"
            :key="article.id"
            class="group cursor-pointer border-b border-gray-100 pb-8 last:border-b-0"
            @click="navigateToArticle(article)"
          >
            <div class="space-y-4">
              <!-- Small Thumbnail -->
              <div class="aspect-[16/9] overflow-hidden rounded-md">
                <img
                  v-if="article.hero_image"
                  :src="article.hero_image.file"
                  :alt="article.hero_image.alt_text || article.title"
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  loading="lazy"
                />
                <div v-else class="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                  <NewspaperIcon class="h-8 w-8 text-gray-400" />
                </div>
              </div>

              <div class="space-y-2">
                <div v-if="article.topic" class="inline-block">
                  <span
                    class="px-2 py-1 text-xs font-medium uppercase tracking-wide rounded-sm text-white"
                    :style="{ backgroundColor: article.topic.color }"
                  >
                    {{ article.topic.name }}
                  </span>
                </div>

                <h3 class="text-xl font-bold text-gray-900 group-hover:text-red-500 transition-colors leading-tight line-clamp-3">
                  {{ article.title }}
                </h3>

                <p class="text-base text-gray-600 leading-relaxed line-clamp-2">
                  {{ article.excerpt }}
                </p>

                <div class="flex items-center space-x-2 text-sm text-gray-500 pt-2">
                  <div class="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
                    <span class="text-xs font-bold text-white uppercase">
                      {{ article.author.username.charAt(0) }}
                    </span>
                  </div>
                  <span class="font-medium">{{ article.author.username }}</span>
                  <span class="text-gray-400">•</span>
                  <time v-if="article.published_at" :datetime="article.published_at">
                    {{ formatDate(article.published_at!) }}
                  </time>
                </div>
              </div>
            </div>
          </article>
        </div>

      <!-- Trending Articles Widget -->
      <section class="py-8 border-b border-gray-200 bg-gray-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-bold text-gray-900">Trending Now</h3>
            <div class="flex items-center space-x-2 text-sm text-gray-500">
              <div class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span>Updated hourly</span>
            </div>
          </div>

          <div class="flex space-x-6 overflow-x-auto pb-4 scrollbar-hide">
            <article
              v-for="article in featuredArticles.slice(0, 4)"
              :key="`trending-${article.id}`"
              class="flex-shrink-0 w-64 group cursor-pointer"
              @click="navigateToArticle(article)"
            >
              <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
                <div class="aspect-[16/10] overflow-hidden">
                  <img
                    v-if="article.hero_image"
                    :src="article.hero_image.file"
                    :alt="article.hero_image.alt_text || article.title"
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    loading="lazy"
                  />
                  <div v-else class="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                    <NewspaperIcon class="h-8 w-8 text-gray-400" />
                  </div>
                </div>

                <div class="p-4">
                  <div v-if="article.topic" class="mb-2">
                    <span
                      class="px-2 py-1 text-xs font-medium rounded text-white"
                      :style="{ backgroundColor: article.topic.color }"
                    >
                      {{ article.topic.name }}
                    </span>
                  </div>

                  <h4 class="text-sm font-bold text-gray-900 group-hover:text-red-500 transition-colors line-clamp-2 leading-tight mb-2">
                    {{ article.title }}
                  </h4>

                  <div class="flex items-center text-xs text-gray-500">
                    <span>{{ article.author.username }}</span>
                    <span class="mx-1">•</span>
                    <span>{{ article.reading_time }} min</span>
                  </div>
                </div>
              </div>
            </article>
          </div>
        </div>
      </section>

      <!-- Latest Articles Section -->
      <section class="py-12 border-t border-gray-200">
        <div class="flex items-center justify-between mb-8">
          <h2 class="text-2xl font-bold text-gray-900">
            {{ selectedCategory ? `${getCategoryName(selectedCategory)} Articles` : 'Latest Articles' }}
          </h2>

          <div v-if="selectedCategory" class="flex items-center space-x-4">
            <span class="text-sm text-gray-600">{{ articleStats.total }} articles</span>
            <button
              @click="clearCategoryFilter"
              class="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center space-x-1"
            >
              <span>View All</span>
              <XMarkIcon class="h-4 w-4" />
            </button>
          </div>
        </div>

        <!-- Advanced Skeleton Loading State -->
        <div v-if="loading" class="space-y-12">
          <!-- Featured Article Skeleton -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-16">
            <div class="space-y-6">
              <div class="h-8 bg-gray-200 rounded w-32 animate-pulse"></div>
              <div class="space-y-4">
                <div class="h-16 bg-gray-200 rounded animate-pulse"></div>
                <div class="h-16 bg-gray-200 rounded animate-pulse"></div>
                <div class="h-12 bg-gray-200 rounded animate-pulse w-3/4"></div>
              </div>
              <div class="flex items-center space-x-6">
                <div class="w-10 h-10 bg-gray-200 rounded-full animate-pulse"></div>
                <div class="space-y-2">
                  <div class="h-4 bg-gray-200 rounded w-24 animate-pulse"></div>
                  <div class="h-3 bg-gray-200 rounded w-32 animate-pulse"></div>
                </div>
              </div>
            </div>
            <div class="aspect-[4/3] bg-gray-200 rounded-lg animate-pulse"></div>
          </div>

          <!-- Article List Skeleton -->
          <div v-for="i in 3" :key="i" class="border-b border-gray-100 pb-12">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div class="lg:col-span-2 space-y-4">
                <div class="h-6 bg-gray-200 rounded w-24 animate-pulse"></div>
                <div class="space-y-3">
                  <div class="h-8 bg-gray-200 rounded animate-pulse"></div>
                  <div class="h-8 bg-gray-200 rounded w-4/5 animate-pulse"></div>
                </div>
                <div class="h-6 bg-gray-200 rounded animate-pulse"></div>
                <div class="flex items-center space-x-4">
                  <div class="w-8 h-8 bg-gray-200 rounded-full animate-pulse"></div>
                  <div class="space-y-1">
                    <div class="h-4 bg-gray-200 rounded w-20 animate-pulse"></div>
                    <div class="h-3 bg-gray-200 rounded w-24 animate-pulse"></div>
                  </div>
                </div>
              </div>
              <div class="aspect-[4/3] bg-gray-200 rounded-lg animate-pulse"></div>
            </div>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="text-center py-12">
          <p class="text-red-600 mb-4">{{ error }}</p>
          <Button @click="() => loadArticles(false)" variant="primary">
            Try Again
          </Button>
        </div>

        <!-- TechCrunch-style Articles List -->
        <div v-else-if="articles.length > 0" class="space-y-12">
          <article
            v-for="article in articles"
            :key="article.id"
            class="group cursor-pointer border-b border-gray-100 pb-12 last:border-b-0"
            @click="navigateToArticle(article)"
          >
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <!-- Article Content -->
              <div class="lg:col-span-2 space-y-4">
                <div v-if="article.topic" class="inline-block">
                  <span
                    class="px-3 py-1 text-xs font-semibold uppercase tracking-wide rounded-md text-white"
                    :style="{ backgroundColor: article.topic.color }"
                  >
                    {{ article.topic.name }}
                  </span>
                </div>

                <h3 class="text-2xl lg:text-3xl font-black text-gray-900 group-hover:text-red-500 transition-colors leading-tight line-clamp-3">
                  {{ article.title }}
                </h3>

                <p class="text-lg text-gray-600 leading-relaxed line-clamp-3">
                  {{ article.excerpt }}
                </p>

                <div class="flex items-center space-x-4 text-sm text-gray-500 pt-4">
                  <div class="flex items-center space-x-2">
                    <div class="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                      <span class="text-xs font-bold text-white uppercase">
                        {{ article.author.username.charAt(0) }}
                      </span>
                    </div>
                    <div>
                      <span class="font-semibold text-gray-900">{{ article.author.username }}</span>
                    </div>
                  </div>

                  <span class="text-gray-400">•</span>

                  <time v-if="article.published_at" :datetime="article.published_at">
                    {{ formatDate(article.published_at!) }}
                  </time>

                  <span class="text-gray-400">•</span>

                  <span>{{ article.reading_time }} min read</span>
                </div>
              </div>

              <!-- Article Image -->
              <div class="lg:col-span-1">
                <div class="aspect-[4/3] overflow-hidden rounded-lg">
                  <img
                    v-if="article.hero_image"
                    :src="article.hero_image.file"
                    :alt="article.hero_image.alt_text || article.title"
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div v-else class="w-full h-full bg-gradient-to-br from-red-50 to-red-100 flex items-center justify-center">
                    <NewspaperIcon class="h-16 w-16 text-red-200" />
                  </div>
                </div>
              </div>
            </div>
          </article>
        </div>

        <!-- Load More -->
        <div v-if="hasMoreArticles" class="text-center mt-12">
          <Button
            @click="loadMoreArticles"
            :loading="loadingMore"
            variant="secondary"
            size="lg"
          >
            Load More Articles
          </Button>
        </div>

        <!-- Empty State -->
        <div v-else-if="!loading && articles.length === 0" class="text-center py-12">
          <NewspaperIcon class="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h3 class="text-lg font-medium text-gray-900 mb-2">No articles found</h3>
          <p class="text-gray-600 mb-6">
            {{ selectedCategory ? 'No articles in this category yet.' : 'Be the first to publish an article!' }}
          </p>
          <router-link to="/login">
            <Button variant="primary" size="lg">
              Start Writing
            </Button>
          </router-link>
        </div>
      </section>

      <!-- TechCrunch-style Newsletter Signup -->
      <section v-if="featuredArticles.length === 0" class="py-16 bg-red-50 border-t border-red-100">
        <div class="max-w-3xl mx-auto text-center">
          <h3 class="text-3xl font-black text-gray-900 mb-6">
            The Latest in Tech & Business
          </h3>
          <p class="text-lg text-gray-600 mb-8 leading-relaxed">
            Get the best tech news, analysis, and insights delivered directly to your inbox. Join over 10 million readers who trust TechCrunch for their daily news briefing.
          </p>
          <div class="flex flex-col sm:flex-row gap-4 max-w-lg mx-auto">
            <input
              v-model="newsletterEmail"
              type="email"
              placeholder="Enter your email address"
              class="flex-1 px-4 py-3 text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-colors"
            >
            <Button
              @click="subscribeNewsletter"
              class="!bg-red-500 hover:!bg-red-600 text-white px-8 py-3 font-semibold rounded-lg transition-colors"
            >
              Subscribe Now
            </Button>
          </div>
          <p class="text-sm text-gray-500 mt-4">
            No spam. Unsubscribe anytime. By subscribing, you agree to our Privacy Policy.
          </p>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <router-link to="/" class="text-xl font-bold mb-4 block">Chronicle</router-link>
            <p class="text-gray-400 text-sm">
              A modern multi-tenant blog platform built for writers, journalists, and creators.
            </p>
          </div>

          <div>
            <h4 class="font-semibold mb-4">Platform</h4>
            <ul class="space-y-2 text-sm text-gray-400">
              <li><router-link to="/" class="hover:text-white transition-colors">Home</router-link></li>
              <li><router-link to="/search" class="hover:text-white transition-colors">Search</router-link></li>
              <li><router-link to="/login" class="hover:text-white transition-colors">Sign In</router-link></li>
              <li><router-link to="/register" class="hover:text-white transition-colors">Start Writing</router-link></li>
            </ul>
          </div>

          <div>
            <h4 class="font-semibold mb-4">Categories</h4>
            <ul class="space-y-2 text-sm text-gray-400">
              <li v-for="category in categories.slice(0, 5)" :key="category.slug">
                <button
                  @click="filterByCategory(category.slug)"
                  class="hover:text-white transition-colors"
                >
                  {{ category.name }}
                </button>
              </li>
            </ul>
          </div>

          <div>
            <h4 class="font-semibold mb-4">Company</h4>
            <ul class="space-y-2 text-sm text-gray-400">
              <li><a href="#" class="hover:text-white transition-colors">About</a></li>
              <li><a href="#" class="hover:text-white transition-colors">Privacy</a></li>
              <li><a href="#" class="hover:text-white transition-colors">Terms</a></li>
              <li><a href="#" class="hover:text-white transition-colors">Contact</a></li>
            </ul>
          </div>
        </div>

        <div class="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400 text-sm">
          <p>&copy; 2025 Chronicle. Built with Vue 3 and Django.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
// Extend window interface for gtag
declare global {
  interface Window {
    gtag?: (command: string, targetId: string, config?: any) => void
  }
}

import { ref, computed, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { NewspaperIcon, MagnifyingGlassIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import type { Article } from '@/types/api'
import { apiClient } from '@/services/api/config'
import Button from '@/components/ui/Button.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

// Advanced image loading with intersection observer
let imageObserver: IntersectionObserver | null = null

const createImageObserver = () => {
  imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target as HTMLImageElement
        if (img.dataset.src) {
          img.src = img.dataset.src
          img.classList.remove('blur-sm')
          img.classList.add('blur-0')
        }
        imageObserver?.unobserve(img)
      }
    })
  }, { threshold: 0.1, rootMargin: '50px' })
}

const observeImages = () => {
  nextTick(() => {
    const images = document.querySelectorAll('.lazy-image')
    images.forEach(img => imageObserver?.observe(img))
  })
}

// Smooth scroll animation
const smoothScrollTo = (element: Element, duration: number = 300) => {
  const start = window.pageYOffset
  const end = element.getBoundingClientRect().top + window.pageYOffset
  const distance = end - start
  let startTime: number | null = null

  const animation = (currentTime: number) => {
    if (startTime === null) startTime = currentTime
    const timeElapsed = currentTime - startTime
    const progress = Math.min(timeElapsed / duration, 1)

    // Easing function
    const easeInOutCubic = (t: number) => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1
    const run = easeInOutCubic(progress)

    window.scrollTo(0, start + distance * run)

    if (timeElapsed < duration) {
      requestAnimationFrame(animation)
    }
  }

  requestAnimationFrame(animation)
}

// Meta management
const updateMetaTags = () => {
  const title = 'Chronicle - Latest Tech News, Analysis & Insights'
  const description = 'Get the latest tech news, business analysis, and insights. Discover stories from independent journalists and creators on the forefront of innovation.'
  const url = window.location.origin
  const image = `${url}/og-image.jpg` // Would need to generate this

  // Update title
  document.title = title

  // Remove existing meta tags
  const existingMeta = document.querySelectorAll('meta[name="description"], meta[property^="og:"], meta[name="twitter:"]')
  existingMeta.forEach(tag => tag.remove())

  // Schema.org structured data
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "NewsMediaOrganization",
    "name": "Chronicle",
    "description": description,
    "url": url,
    "logo": `${url}/logo.png`,
    "sameAs": [
      "https://twitter.com/chronicleapp",
      "https://linkedin.com/company/chronicle"
    ]
  }

  // Create new meta tags
  const metaTags = [
    // Basic SEO
    { name: 'description', content: description },
    { name: 'author', content: 'Chronicle' },
    { name: 'robots', content: 'index, follow' },

    // Open Graph
    { property: 'og:title', content: title },
    { property: 'og:description', content: description },
    { property: 'og:type', content: 'website' },
    { property: 'og:url', content: url },
    { property: 'og:image', content: image },
    { property: 'og:image:width', content: '1200' },
    { property: 'og:image:height', content: '630' },
    { property: 'og:site_name', content: 'Chronicle' },

    // Twitter Card
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:title', content: title },
    { name: 'twitter:description', content: description },
    { name: 'twitter:image', content: image },
    { name: 'twitter:site', content: '@chronicleapp' },
  ]

  // Insert meta tags
  metaTags.forEach(({ name, property, content }) => {
    const meta = document.createElement('meta')
    if (name) meta.setAttribute('name', name)
    if (property) meta.setAttribute('property', property)
    meta.setAttribute('content', content)
    document.head.appendChild(meta)
  })

  // Structured data
  const script = document.createElement('script')
  script.type = 'application/ld+json'
  script.textContent = JSON.stringify(structuredData)
  document.head.appendChild(script)

  // Canonical URL
  let canonicalLink = document.querySelector('link[rel="canonical"]') as HTMLLinkElement
  if (!canonicalLink) {
    canonicalLink = document.createElement('link')
    canonicalLink.rel = 'canonical'
    document.head.appendChild(canonicalLink)
  }
  canonicalLink.href = url
}

const router = useRouter()

// Define interfaces
interface Category {
  name: string
  slug: string
}

interface ArticleStats {
  total: number
  featured: number
}

// Reactive state
const searchQuery = ref('')
const selectedCategory = ref('')
const showSearch = ref(false)
const showMobileNav = ref(false)
const loading = ref(true)
const loadingMore = ref(false)
const error = ref<string | null>(null)
const newsletterEmail = ref('')

// Articles data
const articles = ref<Article[]>([])
const featuredArticles = ref<Article[]>([])
const articleStats = ref<ArticleStats>({ total: 0, featured: 0 })
const currentPage = ref(1)
const hasMoreArticles = ref(false)

// Categories (TechCrunch-style topics)
const categories = ref<Category[]>([
  { name: 'Technology', slug: 'technology' },
  { name: 'Business', slug: 'business' },
  { name: 'Politics', slug: 'politics' },
  { name: 'Health', slug: 'health' },
  { name: 'Lifestyle', slug: 'lifestyle' },
  { name: 'Entertainment', slug: 'entertainment' }
])

// Computed properties
const filteredArticles = computed(() => {
  let articlesList = articles.value

  if (searchQuery.value) {
    articlesList = articlesList.filter((article: Article) =>
      article.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      article.excerpt?.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (selectedCategory.value) {
    articlesList = articlesList.filter((article: Article) =>
      article.topic?.slug === selectedCategory.value
    )
  }

  return articlesList
})

const getCategoryName = (slug: string): string => {
  const category = categories.value.find(cat => cat.slug === slug)
  return category?.name || 'Category'
}

// Methods
const formatViewCount = (count: number): string => {
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(1)}M views`
  } else if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}K views`
  } else {
    return `${count} views`
  }
}

const shareOnTwitter = (article: Article) => {
  const url = encodeURIComponent(`${window.location.origin}/article/${article.id}`)
  const text = encodeURIComponent(`Check out: ${article.title}`)
  const twitterUrl = `https://twitter.com/intent/tweet?url=${url}&text=${text}&via=chronicleapp`
  window.open(twitterUrl, '_blank', 'noopener,noreferrer')
}

const shareOnLinkedIn = (article: Article) => {
  const url = encodeURIComponent(`${window.location.origin}/article/${article.id}`)
  const title = encodeURIComponent(article.title)
  const summary = encodeURIComponent(article.excerpt || '')
  const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}&title=${title}&summary=${summary}`
  window.open(linkedInUrl, '_blank', 'noopener,noreferrer')
}

const formatDate = (dateString: string): string => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - date.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 1) {
    return 'Yesterday'
  } else if (diffDays <= 7) {
    return `${diffDays} days ago`
  } else {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    })
  }
}

const navigateToArticle = (article: Article) => {
  if (article.slug) {
    // Find which account this article belongs to
    // For now, assume we need to route to account-specific article
    // This would need backend support to get account slug from article
    router.push(`/article/${article.id}`) // Placeholder routing
  }
}

const filterByCategory = (slug: string) => {
  selectedCategory.value = slug
  loadArticles()
}

const clearCategoryFilter = () => {
  selectedCategory.value = ''
  loadArticles()
}

const loadArticles = async (append: boolean = false) => {
  if (!append) {
    loading.value = true
    currentPage.value = 1
  } else {
    loadingMore.value = true
  }

  error.value = null

  try {
    const params = new URLSearchParams()
    params.append('page', currentPage.value.toString())
    params.append('featured', 'true')

    if (selectedCategory.value) {
      params.append('topic__slug', selectedCategory.value)
    }

    const response = await apiClient.get(`/articles/public/?${params.toString()}`)

    if (append) {
      articles.value = [...articles.value, ...response.data.results]
    } else {
      articles.value = response.data.results
      featuredArticles.value = response.data.featured || []
    }

    articleStats.value = {
      total: response.data.count || 0,
      featured: response.data.featured_count || 0
    }

    hasMoreArticles.value = !!response.data.next
  } catch (err: any) {
    error.value = err?.response?.data?.error || err.response?.data?.message || err.message || 'Failed to load articles'
    console.error('Error fetching articles:', err)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMoreArticles = async () => {
  currentPage.value++
  await loadArticles(true)
}

const performSearch = () => {
  loadArticles()
  showSearch.value = false
}

const subscribeNewsletter = async () => {
  if (!newsletterEmail.value.trim()) return

  try {
    await apiClient.post('/newsletter/subscribe/', {
      email: newsletterEmail.value.trim()
    })
    newsletterEmail.value = ''
    // Show success message (would need notification system)
    console.log('Newsletter subscription successful')
  } catch (err: any) {
    console.error('Newsletter subscription failed:', err)
  }
}

// Lifecycle
onMounted(async () => {
  const startTime = performance.now()
  updateMetaTags()
  await loadArticles()

  // Performance monitoring
  const loadTime = performance.now() - startTime
  // Log performance in production
  if (import.meta.env.PROD) {
    console.log(`Homepage loaded in ${loadTime.toFixed(2)}ms`)
    // Send to analytics service
    if (window.gtag) {
      window.gtag?.('event', 'page_load_performance', {
        page_title: document.title,
        load_time: loadTime,
        event_category: 'performance'
      })
    }
  }

  // User engagement tracking
  trackUserEngagement()
})

// User engagement and analytics
const trackUserEngagement = () => {
  if (import.meta.env.PROD && window.gtag) {
    // Track initial page view
    window.gtag?.('event', 'page_view', {
      page_title: document.title,
      page_location: window.location.href,
      event_category: 'engagement'
    })

    // Track scroll depth
    let maxScrollDepth = 0
    const trackScroll = () => {
      const scrollTop = window.pageYOffset
      const docHeight = document.documentElement.scrollHeight - window.innerHeight
      const scrollPercent = Math.round((scrollTop / docHeight) * 100)

      if (scrollPercent > maxScrollDepth && scrollPercent % 25 === 0) {
        maxScrollDepth = scrollPercent
        window.gtag?.('event', 'scroll_depth', {
          scroll_depth: scrollPercent,
          event_category: 'engagement'
        })
      }
    }

    window.addEventListener('scroll', trackScroll)

    // Track article clicks
    const trackArticleClicks = () => {
      const articles = document.querySelectorAll('[data-article-id]')
      articles.forEach(article => {
        article.addEventListener('click', () => {
          const articleId = article.getAttribute('data-article-id')
          const articleTitle = article.getAttribute('data-article-title')
          if (window.gtag && articleId && articleTitle) {
            window.gtag?.('event', 'article_click', {
              article_id: articleId,
              article_title: articleTitle,
              event_category: 'engagement'
            })
          }
        })
      })
    }

    // Track after content loads
    nextTick(() => {
      trackArticleClicks()
    })
  }
}

onUnmounted(() => {
  // Clean up any meta tags we added
  const structuredScripts = document.querySelectorAll('script[type="application/ld+json"]')
  structuredScripts.forEach(script => script.remove())
})

// Watch for search query changes and debounce the API call
let searchTimeout: number | null = null
watch(searchQuery, () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    loadArticles()
  }, 300) // 300ms debounce
})
</script>
