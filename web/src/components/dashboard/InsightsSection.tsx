'use client'

import React from 'react'
import { gql, useQuery } from '@apollo/client'
import { Loader2, Lightbulb } from 'lucide-react'

const SUMMARIZE_JOURNALS_QUERY = gql`
    query SummarizeJournals {
        summarizeJournals {
            summary
            generatedAt
        }
    }
`

const dummyInsight = "Based on your recent entries, you've shown a consistent focus on improving your morning routine. You mentioned feeling more energetic on days you wake up early and read. However, you've also noted challenges with staying consistent over the weekend. Perhaps setting a smaller, more achievable weekend goal could help maintain momentum."

export function InsightsSection() {
    const { data, loading, error } = useQuery(SUMMARIZE_JOURNALS_QUERY)

    const renderContent = () => {
        if (loading) {
            return (
                <div className="flex items-center gap-2 text-gray-500">
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Generating your daily insight...</span>
                </div>
            )
        }

        if (error) {
            // Per instructions, show dummy data on error
            return (
                <p className="text-sm text-gray-700 italic">
                    {dummyInsight}
                </p>
            )
        }

        if (data) {
            return (
                <p className="text-sm text-gray-700">
                    {data.summarizeJournals.summary}
                </p>
            )
        }

        return null
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
            <div className="text-sm text-gray-600 space-y-2">
                {renderContent()}
            </div>
        </div>
    )
} 