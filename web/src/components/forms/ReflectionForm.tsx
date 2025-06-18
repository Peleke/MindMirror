'use client'

import { useState } from 'react'
import { useMutation, useQuery } from '@apollo/client'
import { CREATE_REFLECTION_JOURNAL_ENTRY } from '../../../lib/graphql/mutations'
import { JOURNAL_ENTRY_EXISTS_TODAY, GET_JOURNAL_ENTRIES } from '../../../lib/graphql/queries'
import { Lightbulb, Loader2, CheckCircle, Smile, Meh, Frown } from 'lucide-react'

interface ReflectionFormData {
  wins: string[]
  improvements: string[]
  mood: number
}

export function ReflectionForm() {
  const [formData, setFormData] = useState<ReflectionFormData>({
    wins: ['', '', ''],
    improvements: ['', ''],
    mood: 5
  })
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const { data: existsData, loading: existsLoading } = useQuery(JOURNAL_ENTRY_EXISTS_TODAY, {
    variables: { entryType: 'reflection' }
  })

  const [createEntry, { loading: creating, error }] = useMutation(CREATE_REFLECTION_JOURNAL_ENTRY, {
    refetchQueries: [{ query: GET_JOURNAL_ENTRIES }],
    onCompleted: () => {
      setIsSubmitted(true)
      setSubmitError(null)
    },
    onError: (error) => {
      setSubmitError(`GraphQL Error: ${error.message}`)
    }
  })

  const handleArrayInputChange = (
    field: 'wins' | 'improvements',
    index: number,
    value: string
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].map((item, i) => i === index ? value : item)
    }))
  }

  const handleMoodChange = (value: number) => {
    setFormData(prev => ({ ...prev, mood: value }))
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const inputData = {
      wins: formData.wins.filter(item => item.trim() !== ''),
      improvements: formData.improvements.filter(item => item.trim() !== ''),
      mood: getMoodText(formData.mood)
    }

    if (inputData.wins.length === 0 || inputData.improvements.length === 0) {
      setSubmitError('Please fill out at least one win and one area for improvement.')
      return
    }

    try {
      setSubmitError(null)
      await createEntry({
        variables: { input: inputData }
      })
    } catch (err: any) {
      setSubmitError(`Submission failed: ${err.message}`)
    }
  }

  const getMoodIcon = (mood: number) => {
    if (mood >= 7) return <Smile className="w-5 h-5 text-green-600" />
    if (mood >= 4) return <Meh className="w-5 h-5 text-yellow-600" />
    return <Frown className="w-5 h-5 text-red-600" />
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
          You've already reflected today!
        </h3>
        <p className="text-green-700">
          Your evening reflection is complete. See you tomorrow!
        </p>
      </div>
    )
  }

  if (isSubmitted) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-2xl p-8 text-center">
        <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-green-900 mb-2">
          Reflection saved!
        </h3>
        <p className="text-green-700">
          Your thoughts have been recorded. Great job on another day of growth.
        </p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Lightbulb className="w-8 h-8 text-yellow-500" />
          <h1 className="text-3xl font-bold text-gray-900">Evening Reflection</h1>
        </div>
        <p className="text-gray-600">
          Reflect on your day, celebrate your wins, and identify areas for growth.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Wins Section */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            What were your wins today?
          </h3>
          <div className="space-y-3">
            {formData.wins.map((item, index) => (
              <input
                key={index}
                type="text"
                value={item}
                onChange={(e) => handleArrayInputChange('wins', index, e.target.value)}
                placeholder={`A win or success #${index + 1}`}
                className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:border-green-500 focus:ring-4 focus:ring-green-500/20 outline-none transition-all"
              />
            ))}
          </div>
        </div>

        {/* Improvements Section */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            What could have gone better?
          </h3>
          <div className="space-y-3">
            {formData.improvements.map((item, index) => (
              <input
                key={index}
                type="text"
                value={item}
                onChange={(e) => handleArrayInputChange('improvements', index, e.target.value)}
                placeholder={`Area for improvement #${index + 1}`}
                className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 outline-none transition-all"
              />
            ))}
          </div>
        </div>

        {/* Mood Section */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            How are you feeling now?
          </h3>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              {getMoodIcon(formData.mood)}
              <span className="text-lg font-medium text-gray-700">
                {getMoodText(formData.mood)} ({formData.mood}/10)
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              value={formData.mood}
              onChange={(e) => handleMoodChange(Number(e.target.value))}
              className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer mood-slider-yellow"
            />
             <div className="flex justify-between text-xs text-gray-500 mt-2">
                <span>Struggling</span>
                <span>Okay</span>
                <span>Excellent</span>
              </div>
          </div>
        </div>
        
        {(submitError || error) && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h4 className="font-medium text-red-900 mb-2">Error Saving Reflection:</h4>
            {submitError && <p className="text-red-700 text-sm">{submitError}</p>}
            {error && <p className="text-red-700 text-sm">{error.message}</p>}
          </div>
        )}

        <button
          type="submit"
          disabled={creating}
          className="w-full py-4 px-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {creating ? (
            <div className="flex items-center justify-center gap-2">
              <Loader2 className="w-5 h-5 animate-spin" />
              Saving Reflection...
            </div>
          ) : (
            'Save Evening Reflection'
          )}
        </button>
      </form>

       <style jsx>{`
        .mood-slider-yellow::-webkit-slider-thumb {
          appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: linear-gradient(135deg, #3b82f6, #8b5cf6);
          cursor: pointer;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .mood-slider-yellow::-moz-range-thumb {
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: linear-gradient(135deg, #3b82f6, #8b5cf6);
          cursor: pointer;
          border: none;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
      `}</style>
    </div>
  )
} 