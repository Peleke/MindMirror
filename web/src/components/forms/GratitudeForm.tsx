'use client'

import { useState, useEffect } from 'react'
import { useMutation, useQuery } from '@apollo/client'
import { CREATE_GRATITUDE_JOURNAL_ENTRY } from '../../../lib/graphql/mutations'
import { JOURNAL_ENTRY_EXISTS_TODAY } from '../../../lib/graphql/queries'
import { useTradition } from '../../../lib/tradition-context'
import { Heart, Loader2, CheckCircle, Smile, Meh, Frown, Target, Sparkles } from 'lucide-react'

interface GratitudeFormData {
  gratefulFor: string[]
  excitedAbout: string[]
  focus: string
  affirmation: string
  mood: number
}

export function GratitudeForm() {
  const { selectedTradition } = useTradition()
  const [formData, setFormData] = useState<GratitudeFormData>({
    gratefulFor: ['', '', ''],
    excitedAbout: ['', '', ''],
    focus: '',
    affirmation: '',
    mood: 5
  })
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  // Check if entry exists for today
  const { data: existsData, loading: existsLoading } = useQuery(JOURNAL_ENTRY_EXISTS_TODAY, {
    variables: { entryType: 'gratitude' }
  })

  // Create gratitude entry mutation
  const [createEntry, { loading: creating, error }] = useMutation(CREATE_GRATITUDE_JOURNAL_ENTRY, {
    onCompleted: () => {
      setIsSubmitted(true)
      setSubmitError(null)
    },
    onError: (error) => {
      setSubmitError(`GraphQL Error: ${error.message}`)
    }
  })

  // Handle input changes
  const handleArrayInputChange = (
    field: 'gratefulFor' | 'excitedAbout',
    index: number,
    value: string
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].map((item, i) => i === index ? value : item)
    }))
  }

  const handleStringInputChange = (field: 'focus' | 'affirmation', value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleMoodChange = (value: number) => {
    setFormData(prev => ({ ...prev, mood: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Prepare data matching GraphQL schema
    const inputData = {
      gratefulFor: formData.gratefulFor.filter(item => item.trim() !== ''),
      excitedAbout: formData.excitedAbout.filter(item => item.trim() !== ''),
      focus: formData.focus.trim(),
      affirmation: formData.affirmation.trim(),
      mood: getMoodText(formData.mood) // Convert number to string
    }

    // Validation
    if (inputData.gratefulFor.length === 0) {
      setSubmitError('Please add at least one thing you\'re grateful for')
      return
    }
    if (inputData.excitedAbout.length === 0) {
      setSubmitError('Please add at least one thing you\'re excited about')
      return
    }
    if (!inputData.focus) {
      setSubmitError('Please add your main focus for today')
      return
    }
    if (!inputData.affirmation) {
      setSubmitError('Please add your daily affirmation')
      return
    }

    try {
      setSubmitError(null) // Clear any previous errors
      await createEntry({
        variables: {
          input: inputData
        }
      })
    } catch (err: any) {
      console.error('=== GRATITUDE ENTRY ERROR ===')
      console.error('Full error object:', err)
      console.error('Data being sent:', inputData)
      console.error('GraphQL errors:', err.graphQLErrors)
      console.error('Network error:', err.networkError)
      console.error('Error message:', err.message)
      
      // Log the actual HTTP response if available
      if (err.networkError?.result) {
        console.error('HTTP response:', err.networkError.result)
      }
      
      // Log the status code
      if (err.networkError?.statusCode) {
        console.error('HTTP status code:', err.networkError.statusCode)
      }
      
      // Set visual error message
      setSubmitError(`Submission failed: ${err.message}`)
    }
  }

  const getMoodIcon = (mood: number) => {
    if (mood >= 7) return <Smile className="w-5 h-5 text-green-600" />
    if (mood >= 4) return <Meh className="w-5 h-5 text-yellow-600" />
    return <Frown className="w-5 h-5 text-red-600" />
  }

  const getMoodText = (mood: number) => {
    if (mood >= 8) return 'Excellent'
    if (mood >= 7) return 'Great'
    if (mood >= 6) return 'Good'
    if (mood >= 5) return 'Okay'
    if (mood >= 4) return 'Meh'
    if (mood >= 3) return 'Not great'
    return 'Struggling'
  }

  if (existsLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Checking today's entry...</span>
      </div>
    )
  }

  if (existsData?.journalEntryExistsToday) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-2xl p-8 text-center">
        <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-green-900 mb-2">
          Already completed today!
        </h3>
        <p className="text-green-700">
          You've already recorded your gratitude for today. Come back tomorrow for a fresh start!
        </p>
      </div>
    )
  }

  if (isSubmitted) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-2xl p-8 text-center">
        <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-green-900 mb-2">
          Gratitude saved successfully!
        </h3>
        <p className="text-green-700">
          Thank you for taking time to reflect. Your gratitude has been recorded for today.
        </p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Heart className="w-8 h-8 text-red-500" />
          <h1 className="text-3xl font-bold text-gray-900">Morning Gratitude</h1>
        </div>
        <p className="text-gray-600">
          Start your day by reflecting on what you're grateful for and setting positive intentions.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Grateful For Section */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            What are you grateful for today?
          </h3>
          <div className="space-y-3">
            {formData.gratefulFor.map((item, index) => (
              <input
                key={index}
                type="text"
                value={item}
                onChange={(e) => handleArrayInputChange('gratefulFor', index, e.target.value)}
                placeholder={`Something you're grateful for #${index + 1}`}
                className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:border-red-500 focus:ring-4 focus:ring-red-500/20 outline-none transition-all"
              />
            ))}
          </div>
        </div>

        {/* Excited About Section */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            What are you excited about?
          </h3>
          <div className="space-y-3">
            {formData.excitedAbout.map((item, index) => (
              <input
                key={index}
                type="text"
                value={item}
                onChange={(e) => handleArrayInputChange('excitedAbout', index, e.target.value)}
                placeholder={`Something you're excited about #${index + 1}`}
                className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 outline-none transition-all"
              />
            ))}
          </div>
        </div>

        {/* Focus Section */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Target className="w-5 h-5 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900">
              Main Focus
            </h3>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            What's your primary focus or intention for today?
          </p>
          <input
            type="text"
            value={formData.focus}
            onChange={(e) => handleStringInputChange('focus', e.target.value)}
            placeholder="My main focus today is..."
            className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:border-purple-500 focus:ring-4 focus:ring-purple-500/20 outline-none transition-all"
            required
          />
        </div>

        {/* Affirmation Section */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-5 h-5 text-yellow-600" />
            <h3 className="text-lg font-semibold text-gray-900">
              Daily Affirmation
            </h3>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Write a positive affirmation to carry you through the day.
          </p>
          <textarea
            value={formData.affirmation}
            onChange={(e) => handleStringInputChange('affirmation', e.target.value)}
            placeholder="I am confident, capable, and ready to..."
            className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:border-yellow-500 focus:ring-4 focus:ring-yellow-500/20 outline-none transition-all resize-none"
            rows={3}
            required
          />
        </div>

        {/* Mood Section */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            How are you feeling?
          </h3>
          <p className="text-sm text-gray-500 mb-4">
            This helps track your emotional patterns over time
          </p>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              {getMoodIcon(formData.mood)}
              <span className="text-lg font-medium text-gray-700">
                {getMoodText(formData.mood)} ({formData.mood}/10)
              </span>
            </div>
            <div className="relative">
              <input
                type="range"
                min="1"
                max="10"
                value={formData.mood}
                onChange={(e) => handleMoodChange(Number(e.target.value))}
                className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer mood-slider"
                role="slider"
                aria-label="Mood rating"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-2">
                <span>Struggling</span>
                <span>Okay</span>
                <span>Excellent</span>
              </div>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {(error || submitError) && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h4 className="font-medium text-red-900 mb-2">Error Details:</h4>
            {submitError && (
              <p className="text-red-700 text-sm mb-2">
                <strong>Submit Error:</strong> {submitError}
              </p>
            )}
            {error && (
              <div className="text-red-700 text-sm">
                <p className="mb-1"><strong>Apollo Error:</strong> {error.message}</p>
                {error.graphQLErrors?.length > 0 && (
                  <div className="mb-2">
                    <strong>GraphQL Errors:</strong>
                    <ul className="list-disc list-inside ml-2">
                      {error.graphQLErrors.map((err, i) => (
                        <li key={i}>{err.message}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {error.networkError && (
                  <p><strong>Network Error:</strong> {error.networkError.message}</p>
                )}
              </div>
            )}
          </div>
        )}

        {/* Submit Button */}
        <div className="space-y-4">
          {/* Debug Button - Temporary */}
          <button
            type="button"
            onClick={() => {
              const inputData = {
                gratefulFor: formData.gratefulFor.filter(item => item.trim() !== ''),
                excitedAbout: formData.excitedAbout.filter(item => item.trim() !== ''),
                focus: formData.focus.trim(),
                affirmation: formData.affirmation.trim(),
                mood: getMoodText(formData.mood)
              }
              console.log('=== DEBUG DATA ===')
              console.log('Input data:', inputData)
              console.log('GraphQL mutation:', CREATE_GRATITUDE_JOURNAL_ENTRY)
              console.log('Selected tradition:', selectedTradition)
            }}
            className="w-full py-3 px-6 bg-gray-500 text-white rounded-xl font-medium"
          >
            🔍 Debug: Log Data (Check Console)
          </button>
          
          <button
            type="submit"
            disabled={creating}
            className="w-full py-4 px-6 bg-gradient-to-r from-red-500 to-pink-500 text-white rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            {creating ? (
              <div className="flex items-center justify-center gap-2">
                <Loader2 className="w-5 h-5 animate-spin" />
                Saving...
              </div>
            ) : (
              'Save Gratitude Entry'
            )}
          </button>
        </div>
      </form>

      <style jsx>{`
        .mood-slider::-webkit-slider-thumb {
          appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: linear-gradient(135deg, #ef4444, #ec4899);
          cursor: pointer;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .mood-slider::-moz-range-thumb {
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: linear-gradient(135deg, #ef4444, #ec4899);
          cursor: pointer;
          border: none;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
      `}</style>
    </div>
  )
} 