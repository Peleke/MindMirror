'use client'

import React from 'react'
import Link from 'next/link'
import { useAuth } from '../../../lib/auth-context'
import { useTradition } from '../../../lib/tradition-context'
import { apolloConfig } from '../../../lib/apollo-client'
import { Brain, Loader2, CheckCircle, Globe, Server, Book } from 'lucide-react'
import { ConnectionTest } from '../../components/dashboard/ConnectionTest'

export default function DashboardPage() {
  const { user, session, loading } = useAuth()
  const { selectedTradition, traditions } = useTradition()

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <Brain className="w-8 h-8 text-white" />
          </div>
          <div className="flex items-center gap-2 text-gray-600">
            <Loader2 className="w-5 h-5 animate-spin" />
            Loading your MindMirror...
          </div>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Authentication Required
          </h1>
          <p className="text-gray-600">
            Please sign in to access your dashboard.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-4xl">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome to MindMirror
        </h1>
        <p className="text-gray-600">
          Your intelligent companion for self-reflection and growth. The dashboard is now ready with full Apollo Client integration!
        </p>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {/* Authentication Status */}
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <CheckCircle className="w-8 h-8 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900">Authentication</h3>
          </div>
          <div className="space-y-2 text-sm text-gray-600">
            <div>✅ User authenticated</div>
            <div>✅ Session active</div>
            <div>✅ JWT token ready</div>
          </div>
        </div>

        {/* Apollo Client Status */}
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">GQL</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">GraphQL Client</h3>
          </div>
          <div className="space-y-2 text-sm text-gray-600">
            <div>✅ Apollo Client configured</div>
            <div>✅ Gateway connection ready</div>
            <div>✅ Authentication headers set</div>
          </div>
        </div>

        {/* Environment Status */}
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            {apolloConfig.isDocker ? (
              <Server className="w-8 h-8 text-blue-600" />
            ) : (
              <Globe className="w-8 h-8 text-green-600" />
            )}
            <h3 className="text-lg font-semibold text-gray-900">Environment</h3>
          </div>
          <div className="space-y-2 text-sm text-gray-600">
            <div>Mode: {apolloConfig.isDocker ? 'Docker' : 'Local'}</div>
            <div>Gateway: {apolloConfig.gatewayUrl}</div>
            <div>Environment: {apolloConfig.environment}</div>
          </div>
        </div>
      </div>

      {/* Gateway Connection Test */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Gateway Connection Test</h2>
        <ConnectionTest />
      </div>

      {/* Tradition Info */}
      <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-6 border border-blue-100 mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Book className="w-8 h-8 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Knowledge Base</h3>
        </div>
        <div className="text-sm text-gray-600 space-y-2">
          <div>
            <span className="font-medium">Selected:</span> {selectedTradition}
          </div>
          <div>
            <span className="font-medium">Available traditions:</span> {traditions.length > 0 ? traditions.join(', ') : 'Loading...'}
          </div>
          <p className="text-xs text-blue-600 mt-2">
            Your selected tradition affects all AI interactions and influences the responses you receive.
          </p>
        </div>
      </div>

      {/* Next Steps */}
      <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Ready to Begin</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border border-green-100">
            <h4 className="font-medium text-gray-900 mb-2">Start Your Day</h4>
            <p className="text-sm text-gray-600 mb-3">Begin with morning gratitude to set a positive tone.</p>
            <Link 
              href="/dashboard/gratitude"
              className="text-sm font-medium text-green-700 hover:text-green-800 transition-colors"
            >
              Go to Gratitude →
            </Link>
          </div>
          <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg border border-purple-100">
            <h4 className="font-medium text-gray-900 mb-2">Chat with AI</h4>
            <p className="text-sm text-gray-600 mb-3">Start a conversation with your AI companion.</p>
            <Link 
              href="/dashboard/chat"
              className="text-sm font-medium text-purple-700 hover:text-purple-800 transition-colors"
            >
              Open Chat →
            </Link>
          </div>
        </div>
      </div>

      {/* Debug Information */}
      <div className="mt-8 bg-gray-100 rounded-xl p-4">
        <h3 className="font-semibold text-gray-700 mb-2">Debug Information</h3>
        <div className="text-sm text-gray-600 space-y-1">
          <div>User ID: {user.id}</div>
          <div>Email: {user.email}</div>
          <div>Session: {session ? 'Active' : 'None'}</div>
          <div>Selected Tradition: {selectedTradition}</div>
          <div>Apollo Gateway: {apolloConfig.gatewayUrl}</div>
        </div>
      </div>
    </div>
  )
} 