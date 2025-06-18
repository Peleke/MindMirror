'use client'

import { useState } from 'react'
import { useMutation, useQuery } from '@apollo/client'
import { CREATE_FREEFORM_JOURNAL_ENTRY } from '../../../lib/graphql/mutations'
import { JOURNAL_ENTRY_EXISTS_TODAY, GET_JOURNAL_ENTRIES } from '../../../lib/graphql/queries'
import { PenTool, Loader2, CheckCircle } from 'lucide-react'

export function FreeformJournalForm() {
  const [content, setContent] = useState('')
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const { data: existsData, loading: existsLoading } = useQuery(JOURNAL_ENTRY_EXISTS_TODAY, {
    variables: { entryType: 'freeform' }
  });

  const [createEntry, { loading: creating, error }] = useMutation(CREATE_FREEFORM_JOURNAL_ENTRY, {
    refetchQueries: [{ query: GET_JOURNAL_ENTRIES }],
    onCompleted: () => {
      setIsSubmitted(true)
      setSubmitError(null)
      setContent('')
    },
    onError: (error) => {
      setSubmitError(`GraphQL Error: ${error.message}`)
    }
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!content.trim()) {
      setSubmitError('Journal content cannot be empty.')
      return
    }

    try {
      setSubmitError(null)
      await createEntry({
        variables: {
          input: { content: content.trim() }
        }
      })
    } catch (err: any) {
      setSubmitError(`Submission failed: ${err.message}`)
    }
  }
  
  if (existsLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading...</span>
      </div>
    )
  }

  // Unlike other forms, we allow multiple freeform entries per day.
  // So, we don't block if existsData.journalEntryExistsToday is true.
  // We could show a notice, but for now, we'll just allow it.

  if (isSubmitted && !creating) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-2xl p-8 text-center max-w-2xl mx-auto">
        <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-green-900 mb-2">
          Entry Saved!
        </h3>
        <p className="text-green-700 mb-4">
          Your thoughts have been recorded.
        </p>
        <button
          onClick={() => setIsSubmitted(false)}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          Write Another Entry
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-3 mb-4">
          <PenTool className="w-8 h-8 text-green-500" />
          <h1 className="text-3xl font-bold text-gray-900">Freeform Journal</h1>
        </div>
        <p className="text-gray-600">
          A blank canvas for your thoughts, ideas, and reflections. Write whatever comes to mind.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white rounded-2xl p-2 border border-gray-200 shadow-sm focus-within:ring-4 focus-within:ring-green-500/20 transition-all">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Let your thoughts flow..."
            className="w-full p-4 border-none outline-none resize-none rounded-xl"
            rows={15}
            disabled={creating}
          />
        </div>

        {(submitError || error) && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h4 className="font-medium text-red-900 mb-2">Error Saving Entry:</h4>
            {submitError && <p className="text-red-700 text-sm">{submitError}</p>}
            {error && <p className="text-red-700 text-sm">{error.message}</p>}
          </div>
        )}

        <button
          type="submit"
          disabled={creating || !content.trim()}
          className="w-full py-4 px-6 bg-gradient-to-r from-green-500 to-teal-500 text-white rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {creating ? (
            <div className="flex items-center justify-center gap-2">
              <Loader2 className="w-5 h-5 animate-spin" />
              Saving Entry...
            </div>
          ) : (
            'Save Journal Entry'
          )}
        </button>
      </form>
    </div>
  )
} 