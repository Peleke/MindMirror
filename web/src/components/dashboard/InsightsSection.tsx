'use client'

import React, { useState, useEffect } from 'react'
import { gql, useQuery } from '@apollo/client'
import { Loader2, Lightbulb, AlertTriangle } from 'lucide-react'

const SUMMARIZE_JOURNALS_QUERY = gql`
    query SummarizeJournals {
        summarizeJournals {
            summary
            generatedAt
        }
    }
`

export function InsightsSection() {
    const { data, loading, error, refetch } = useQuery(SUMMARIZE_JOURNALS_QUERY, {
        fetchPolicy: 'network-only', // Ensures fresh data on each load
        notifyOnNetworkStatusChange: true,
    })
    const [timedOut, setTimedOut] = useState(false)

    // Get timeout from environment variable with fallback to 120 seconds
    const timeoutMs = parseInt(process.env.NEXT_PUBLIC_INSIGHT_TIMEOUT || '120000', 10)

    useEffect(() => {
        if (loading) {
            setTimedOut(false); // Reset timeout on new request
            const timer = setTimeout(() => {
                setTimedOut(true);
            }, timeoutMs);

            return () => clearTimeout(timer);
        }
    }, [loading, timeoutMs]);


    const handleRetry = () => {
        setTimedOut(false)
        refetch()
    }

    const renderContent = () => {
        if (loading && !timedOut) {
            return (
                <div className="flex items-center gap-2 text-gray-500">
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Generating your daily insight...</span>
                </div>
            )
        }

        if (error || timedOut) {
            const errorMessage = timedOut 
                ? "The request timed out. The AI may be busy or unavailable."
                : error?.message || "An unknown error occurred."

            return (
                <div className="flex flex-col items-center text-center gap-3 text-red-700">
                    <AlertTriangle className="w-8 h-8" />
                    <div>
                        <p className="font-semibold">Failed to generate insight.</p>
                        <p className="text-xs mb-4">{errorMessage}</p>
                        <button
                            onClick={handleRetry}
                            className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-semibold hover:bg-red-700"
                        >
                            Retry
                        </button>
                    </div>
                </div>
            )
        }

        if (data?.summarizeJournals?.summary) {
            return (
                <p className="text-sm text-gray-700 italic">
                    {data.summarizeJournals.summary}
                </p>
            )
        }

        return (
            <p className="text-sm text-gray-500">
                No insights available yet. Write a few journal entries to get started.
            </p>
        )
    }

    return (
        <div className="bg-gradient-to-br from-green-50 to-cyan-50 rounded-2xl p-6 border border-green-100 mb-8">
            <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-cyan-500 rounded-xl flex items-center justify-center text-white shadow-md">
                    <Lightbulb className="w-6 h-6" />
                </div>
                <div>
                    <h3 className="text-lg font-semibold text-gray-900">AI-Powered Insight</h3>
                    <p className="text-sm text-gray-500">A summary of your recent journal entries.</p>
                </div>
            </div>
            <div className="text-sm text-gray-600 space-y-2">{renderContent()}</div>
        </div>
    )
} 