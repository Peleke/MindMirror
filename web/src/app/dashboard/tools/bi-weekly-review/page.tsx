'use client'

import { useMutation, gql } from '@apollo/client'
import { AlertTriangle, Bot, Loader2, Sparkles, Wand2 } from 'lucide-react'
import { FreeformResponse } from '@/components/tools/FreeformResponse'


const GENERATE_REVIEW_MUTATION = gql`
    mutation GenerateReview($tradition: String!) {
        generateReview(tradition: $tradition) {
            key_success
            improvement_area
            journal_prompt
        }
    }
`

export default function BiWeeklyReview() {
  const [generateReview, { data, loading, error }] = useMutation(
    GENERATE_REVIEW_MUTATION
  )

  return (
    <div className="container mx-auto p-4">
        <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3"><Bot className="w-8 h-8" /> Bi-Weekly Review</h1>
            <p className="text-gray-600">Generate an AI-powered review of your journal entries from the last 14 days.</p>
        </div>

        <div className="mt-6 text-center">
            <button
                onClick={() => generateReview({ variables: { tradition: 'canon-default' }})}
                disabled={loading}
                className="px-8 py-4 text-lg font-semibold bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transform hover:-translate-y-0.5 transition-all duration-300 rounded-xl inline-flex items-center"
            >
            {loading ? (
                <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Generating Your Review...
                </>
            ) : (
                <>
                <Wand2 className="mr-2 h-5 w-5" />
                Generate My Review
                </>
            )}
            </button>
        </div>

        {error && (
            <div className="mt-6 bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 mt-0.5" />
                <div>
                    <h4 className="font-bold">Failed to Generate Review</h4>
                    <p className="text-sm">{error.message}</p>
                </div>
            </div>
        )}

      {data && (
        <div className="mt-8 space-y-8">
            {data.generateReview.key_success && !data.generateReview.key_success.toLowerCase().includes('error') && (
                 <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                        <Sparkles className="w-6 h-6 text-purple-500" />
                        Your Performance Review
                    </h3>
                    <div className="space-y-4">
                        <div>
                            <h4 className="font-semibold text-green-700">Key Success</h4>
                            <p className="text-gray-600">{data.generateReview.key_success}</p>
                        </div>
                        <div>
                            <h4 className="font-semibold text-amber-700">Improvement Area</h4>
                            <p className="text-gray-600">{data.generateReview.improvement_area}</p>
                        </div>
                    </div>
                </div>
            )}

            {data.generateReview.journal_prompt && (
                <FreeformResponse journalPrompt={data.generateReview.journal_prompt} />
            )}
        </div>
      )}
    </div>
  )
} 