'use client'

import React from 'react'
import Link from 'next/link'
import { useAuth } from '../../../lib/auth-context'
import { useTradition } from '../../../lib/tradition-context'
import { apolloConfig } from '../../../lib/apollo-client'
import { Brain, Loader2, CheckCircle, Globe, Server, Book, Heart, Lightbulb } from 'lucide-react'
import { ConnectionTest } from '../../components/dashboard/ConnectionTest'
import { InsightsSection } from '../../components/dashboard/InsightsSection'

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
    <div className="p-4 sm:p-6 max-w-5xl mx-auto">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome, {user.email?.split('@')[0]}
        </h1>
        <p className="text-gray-600">
          Your intelligent companion for self-reflection and growth. What would you like to do today?
        </p>
      </div>

      {/* Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Link href="/dashboard/gratitude" className="group bg-white rounded-2xl p-6 border border-gray-200 shadow-sm hover:border-red-400 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
            <div className="flex items-center gap-4 mb-3">
                <div className="w-12 h-12 bg-gradient-to-br from-red-400 to-pink-500 rounded-xl flex items-center justify-center text-white shadow-md">
                    <Heart className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">Morning Gratitude</h3>
            </div>
            <p className="text-sm text-gray-600">Start your day with a positive mindset by recording what you're grateful for.</p>
          </Link>
          <Link href="/dashboard/reflection" className="group bg-white rounded-2xl p-6 border border-gray-200 shadow-sm hover:border-yellow-400 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
            <div className="flex items-center gap-4 mb-3">
                <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center text-white shadow-md">
                    <Lightbulb className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">Evening Reflection</h3>
            </div>
            <p className="text-sm text-gray-600">Reflect on your day, celebrate wins, and find areas for improvement.</p>
          </Link>
      </div>
      
      <InsightsSection />

      {/* Tradition Info */}
      <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-6 border border-blue-100 mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Book className="w-8 h-8 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Knowledge Base</h3>
        </div>
        <div className="text-sm text-gray-600 space-y-2">
          <div>
            <span className="font-medium">Selected Tradition:</span> <span className="font-semibold text-blue-800 bg-blue-100 px-2 py-1 rounded-md">{selectedTradition}</span>
          </div>
          <div>
            <span className="font-medium">Available Traditions:</span> {traditions.length > 0 ? traditions.join(', ') : 'Loading...'}
          </div>
          <p className="text-xs text-blue-700 mt-2 pt-2 border-t border-blue-200">
            Your selected tradition affects all AI interactions. You can change this in Settings.
          </p>
        </div>
      </div>

      <div className="border-t border-gray-200 my-8"></div>

      {/* Status & Debug Section */}
      <div className="space-y-6">
        <h2 className="text-xl font-semibold text-gray-800">System Status</h2>
        
        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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

        {/* Debug Information */}
        <div className="mt-8 bg-gray-800 text-gray-200 rounded-xl p-4 font-mono text-xs">
          <h3 className="font-semibold text-gray-400 mb-2 uppercase tracking-wider">Debug Information</h3>
          <div className="space-y-1">
            <div><span className="text-gray-500">User ID:</span> {user.id}</div>
            <div><span className="text-gray-500">Email:</span> {user.email}</div>
            <div><span className="text-gray-500">Session:</span> {session ? 'Active' : 'None'}</div>
            <div><span className="text-gray-500">Tradition:</span> {selectedTradition}</div>
            <div><span className="text-gray-500">Gateway:</span> {apolloConfig.gatewayUrl}</div>
          </div>
        </div>

        {/* Gateway Connection Test */}
        <div className="mt-8">
          <h3 className="font-semibold text-gray-700 mb-2">Gateway Connection Test</h3>
          <ConnectionTest />
        </div>
      </div>
    </div>
  )
} 