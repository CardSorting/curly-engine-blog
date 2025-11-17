import { ref, reactive, computed } from 'vue'
import { useApi } from './useApi'
import { apiClient } from '@/services/api/config'
import { useNotification } from '@kyvg/vue3-notification'

export interface TextAnalysisResults {
  word_count: number
  sentence_count: number
  character_count: number
  flesch_reading_ease: number
  flesch_kincaid_grade: number
  readability_level: string
  grammar_issues: number
  grammar_score: number
  seo_score: number
  overall_score: number
  summary: string[]
  issues?: Array<{
    type: string
    message: string
    severity: 'minor' | 'warning' | 'error'
    position?: number
  }>
  suggestions?: Array<{
    type: string
    title: string
    description: string
    severity: 'low' | 'medium' | 'high'
    position?: number
  }>
}

export interface WritingSuggestion {
  id: string
  title: string
  description: string
  suggestion_text: string
  confidence_score: number
  severity: 'low' | 'medium' | 'high'
}

export const useContentAnalysis = () => {
  const api = useApi()
  const { notify } = useNotification()

  // Reactive state
  const analysisResults = ref<TextAnalysisResults | null>(null)
  const writingSuggestions = ref<WritingSuggestion[]>([])
  const isAnalyzing = ref(false)
  const isGeneratingSuggestions = ref(false)
  const lastAnalysisTime = ref<Date | null>(null)

  // Computed properties
  const hasIssues = computed(() => {
    return analysisResults.value?.issues && analysisResults.value.issues.length > 0
  })

  const issueCountBySeverity = computed(() => {
    if (!analysisResults.value?.issues) return { minor: 0, warning: 0, error: 0 }

    return analysisResults.value.issues.reduce((acc, issue) => {
      acc[issue.severity] = (acc[issue.severity] || 0) + 1
      return acc
    }, { minor: 0, warning: 0, error: 0 } as Record<string, number>)
  })

  const readabilityRating = computed(() => {
    if (!analysisResults.value) return { level: 'unknown', color: 'gray' }

    const score = analysisResults.value.flesch_reading_ease
    const level = analysisResults.value.readability_level

    let color = 'gray'
    if (score >= 80) color = 'green'
    else if (score >= 60) color = 'yellow'
    else if (score >= 30) color = 'orange'
    else color = 'red'

    return { level, color, score }
  })

  // Methods
  const analyzeText = async (
    text: string,
    analysisType: 'grammar' | 'readability' | 'seo' | 'comprehensive' = 'comprehensive',
    language: string = 'en'
  ): Promise<TextAnalysisResults | null> => {
    if (!text || text.trim().length < 10) {
      notify({
        title: 'Text too short',
        text: 'Please enter at least 10 characters for analysis',
        type: 'warning'
      })
      return null
    }

    isAnalyzing.value = true
    try {
      const response = await api.execute(apiClient.post, '/content-analysis/text-analysis/analyze/', {
        text_content: text,
        analysis_type: analysisType,
        language
      }) as any

      analysisResults.value = response.results
      lastAnalysisTime.value = new Date()

      // Auto-generate suggestions if comprehensive analysis
      if (analysisType === 'comprehensive' && response.id) {
        await generateSuggestions(response.id)
      }

      notify({
        title: 'Analysis Complete',
        text: `Found ${analysisResults.value?.issues?.length || 0} issues, readability: ${readabilityRating.value.level}`,
        type: 'success'
      })

      return analysisResults.value
    } catch (error: any) {
      notify({
        title: 'Analysis Failed',
        text: error.response?.data?.detail || 'Unable to analyze text',
        type: 'error'
      })
      return null
    } finally {
      isAnalyzing.value = false
    }
  }

  const realTimeCheck = async (
    text: string,
    checkType: 'grammar' | 'readability' = 'grammar',
    language: string = 'en'
  ): Promise<any> => {
    if (!text || text.trim().length < 5) {
      return { issues: [], score: 100, level: 'Unknown' }
    }

    try {
      const response = await api.execute(apiClient.post, '/content-analysis/realtime-check/', {
        text,
        type: checkType,
        language
      })

      return response
    } catch (error) {
      // Return safe defaults on error
      return { issues: [], score: 100, level: 'Unknown' }
    }
  }

  const generateSuggestions = async (analysisId: string): Promise<WritingSuggestion[]> => {
    if (!analysisId) return []

    isGeneratingSuggestions.value = true
    try {
      const response = await api.execute(apiClient.get, `/content-analysis/text-analysis/${analysisId}/suggestions/`) as any[]

      writingSuggestions.value = response.map((suggestion: any) => ({
        id: suggestion.id,
        title: suggestion.title,
        description: suggestion.description,
        suggestion_text: suggestion.suggestion_text || suggestion.suggested_text,
        confidence_score: suggestion.confidence_score,
        severity: suggestion.severity
      }))

      return writingSuggestions.value
    } catch (error: any) {
      notify({
        title: 'Suggestion Generation Failed',
        text: error.response?.data?.detail || 'Unable to generate suggestions',
        type: 'warning'
      })
      return []
    } finally {
      isGeneratingSuggestions.value = false
    }
  }

  const applySuggestion = async (suggestionId: string, originalText: string): Promise<string> => {
    try {
      const response = await api.execute(apiClient.post, `/content-analysis/suggestions/${suggestionId}/apply/`, {
        original_text: originalText
      }) as any

      notify({
        title: 'Suggestion Applied',
        text: 'Writing suggestion has been applied to your text',
        type: 'success'
      })

      return response.modified_text
    } catch (error: any) {
      notify({
        title: 'Apply Failed',
        text: error.response?.data?.detail || 'Unable to apply suggestion',
        type: 'error'
      })
      return originalText
    }
  }

  const acceptSuggestion = async (suggestionId: string): Promise<boolean> => {
    try {
      await api.execute(apiClient.post, `/content-analysis/suggestions/${suggestionId}/accept/`)
      // Update local suggestion
      const suggestion = writingSuggestions.value.find(s => s.id === suggestionId)
      if (suggestion) {
        Object.assign(suggestion, { accepted: true })
      }
      return true
    } catch (error) {
      return false
    }
  }

  const dismissSuggestion = async (suggestionId: string): Promise<boolean> => {
    try {
      await api.execute(apiClient.post, `/content-analysis/suggestions/${suggestionId}/dismiss/`)
      // Update local suggestion
      const suggestion = writingSuggestions.value.find(s => s.id === suggestionId)
      if (suggestion) {
        Object.assign(suggestion, { dismissed: true })
      }
      return true
    } catch (error) {
      return false
    }
  }

  const clearResults = () => {
    analysisResults.value = null
    writingSuggestions.value = []
    lastAnalysisTime.value = null
  }

  const getReadabilityColor = (score: number): string => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    if (score >= 30) return 'text-orange-600'
    return 'text-red-600'
  }

  const getSeverityColor = (severity: string): string => {
    switch (severity) {
      case 'high':
      case 'error':
        return 'text-red-600 bg-red-50'
      case 'medium':
      case 'warning':
        return 'text-yellow-600 bg-yellow-50'
      case 'low':
      case 'minor':
        return 'text-blue-600 bg-blue-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const getSeverityIcon = (severity: string): string => {
    switch (severity) {
      case 'high':
      case 'error':
        return '⚠️'
      case 'medium':
      case 'warning':
        return '⚡'
      case 'low':
      case 'minor':
        return 'ℹ️'
      default:
        return '💡'
    }
  }

  return {
    // State
    analysisResults,
    writingSuggestions,
    isAnalyzing,
    isGeneratingSuggestions,
    lastAnalysisTime,

    // Computed
    hasIssues,
    issueCountBySeverity,
    readabilityRating,

    // Methods
    analyzeText,
    realTimeCheck,
    generateSuggestions,
    applySuggestion,
    acceptSuggestion,
    dismissSuggestion,
    clearResults,
    getReadabilityColor,
    getSeverityColor,
    getSeverityIcon
  }
}
