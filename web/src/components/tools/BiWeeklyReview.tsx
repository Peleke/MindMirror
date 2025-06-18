'use client'

import { useState } from 'react'
import { useMutation } from '@apollo/client'
import { useTradition } from '../../../lib/tradition-context'
import { GENERATE_REVIEW } from '../../../lib/graphql/mutations'
import { FileText, Loader2, Wand2, CheckCircle, AlertTriangle, Lightbulb, Trophy, Target } from 'lucide-react'

interface ReviewResult {
  keySuccess: string
  improvementArea: string
  journalPrompt: string
}

export function BiWeeklyReview() {
  const { selectedTradition } = useTradition()
  const [result, setResult] = useState<ReviewResult | null>(null)

  const [generateReview, { loading, error }] = useMutation(GENERATE_REVIEW, {
    onCompleted: (data) => {
      if (data?.generateReview) {
        setResult(data.generateReview)
      }
    },
  })

  const handleGenerate = () => {
    setResult(null)
    generateReview({
      variables: {
        tradition: selectedTradition,
      },
    })
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-3 mb-4">
          <FileText className="w-8 h-8 text-indigo-500" />
          <h1 className="text-3xl font-bold text-gray-900">Bi-Weekly Review</h1>
        </div>
        <p className="text-gray-600">
          Generate an AI-powered summary of your key successes, areas for improvement, and a tailored journal prompt based on your recent entries.
        </p>
      </div>

      <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm text-center">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Generate Your Review</h3>
        <p className="text-sm text-gray-600 mb-4">
          This will analyze your journal entries from the last 14 days using the <span className="font-semibold text-indigo-600">{selectedTradition}</span> tradition.
        </p>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <div className="flex items-center justify-center gap-2">
              <Loader2 className="w-5 h-5 animate-spin" />
              Analyzing Entries...
            </div>
          ) : (
            <div className="flex items-center justify-center gap-2">
              <Wand2 className="w-5 h-5" />
              Generate Review
            </div>
          )}
        </button>
      </div>
      
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center mt-6">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="font-semibold text-red-800 mb-2">Failed to Generate Review</h3>
          <p className="text-red-700 text-sm mb-4">There was a problem generating your review. This can happen if there isn't enough journal data in the last 14 days.</p>
          <p className="text-xs text-red-600 bg-red-100 p-2 rounded-md font-mono">{error.message}</p>
        </div>
      )}

      {result && !loading && (
        <div className="mt-8 space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-2xl p-6 text-center">
            <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-green-900">Your Review is Ready!</h2>
          </div>
          
          {/* Key Success */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
            <div className="flex items-center gap-3 mb-3">
              <Trophy className="w-6 h-6 text-yellow-500" />
              <h3 className="text-xl font-semibold text-gray-900">Key Success</h3>
            </div>
            <p className="text-gray-700 leading-relaxed">{result.keySuccess}</p>
          </div>
          
          {/* Improvement Area */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
            <div className="flex items-center gap-3 mb-3">
              <Target className="w-6 h-6 text-blue-500" />
              <h3 className="text-xl font-semibold text-gray-900">Area for Improvement</h3>
            </div>
            <p className="text-gray-700 leading-relaxed">{result.improvementArea}</p>
          </div>

          {/* Journal Prompt */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
            <div className="flex items-center gap-3 mb-3">
              <Lightbulb className="w-6 h-6 text-purple-500" />
              <h3 className="text-xl font-semibold text-gray-900">Personalized Journal Prompt</h3>
            </div>
            <p className="text-gray-700 leading-relaxed italic">"{result.journalPrompt}"</p>
          </div>
        </div>
      )}
    </div>
  )
} 