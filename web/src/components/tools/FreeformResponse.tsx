'use client'

import { useState } from 'react'
import { useMutation, gql } from '@apollo/client'
import { BookCheck, Loader2, AlertTriangle, Send } from 'lucide-react'
import { CREATE_FREEFORM_JOURNAL_ENTRY } from '../../../lib/graphql/mutations'
import { toast } from 'react-hot-toast'

interface FreeformResponseProps {
  journalPrompt: string
}

export function FreeformResponse({ journalPrompt }: FreeformResponseProps) {
  const [content, setContent] = useState('')
  const [createFreeformJournal, { loading, error, data }] = useMutation(
    CREATE_FREEFORM_JOURNAL_ENTRY,
    {
      refetchQueries: ['GetJournalEntries'],
      onCompleted: () => {
        toast.success('Journal entry saved!')
        setContent('')
      },
      onError: (error) => {
        toast.error(`Error saving entry: ${error.message}`)
      }
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!content.trim()) {
        toast.error("Journal entry cannot be empty.")
        return
    }
    createFreeformJournal({
      variables: {
        content: `Prompt: "${journalPrompt}"\n\nResponse: ${content}`,
      },
    })
  }

  if (data) {
    return (
      <div className="bg-teal-50 border border-teal-200 rounded-2xl p-6 text-center">
        <BookCheck className="w-12 h-12 text-teal-600 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-teal-900">Response Saved!</h3>
        <p className="text-teal-800">Your journal entry has been successfully recorded.</p>
      </div>
    )
  }

  return (
    <div className="bg-gray-50 rounded-2xl p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Respond to Your AI Prompt</h3>
        <blockquote className="border-l-4 border-indigo-400 bg-indigo-50 p-4 my-4">
          <p className="italic text-indigo-800">"{journalPrompt}"</p>
        </blockquote>
        <form onSubmit={handleSubmit}>
            <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Write your thoughts here..."
                className="w-full h-32 p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
                disabled={loading}
            />
            <div className="mt-4 flex justify-end items-center gap-4">
                {error && <p className="text-sm text-red-600">Error: {error.message}</p>}
                <button
                    type="submit"
                    disabled={loading || !content.trim()}
                    className="px-5 py-2.5 bg-indigo-600 text-white rounded-lg font-semibold text-sm shadow-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all duration-200"
                >
                    {loading ? (
                        <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span>Saving...</span>
                        </>
                    ) : (
                        <>
                            <Send className="w-4 h-4" />
                            <span>Save Journal</span>
                        </>
                    )}
                </button>
            </div>
        </form>
    </div>
  )
} 