'use client'

import React from 'react'
import { useAuth } from '../../../lib/auth-context'
import { Brain, LogOut, Loader2 } from 'lucide-react'

export default function DashboardPage() {
  const { user, session, loading, signOut } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
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

  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('Error signing out:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center shadow-md">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                MindMirror
              </span>
            </div>

            {/* User Menu */}
            <div className="flex items-center gap-4">
              <div className="text-sm text-gray-600">
                Welcome, <span className="font-semibold">{user.email}</span>
              </div>
              <button
                onClick={handleSignOut}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome to MindMirror
          </h1>
          <p className="text-gray-600">
            Your journey of self-discovery starts here. The core application features are coming soon.
          </p>
        </div>

        {/* Coming Soon */}
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-3xl p-8 text-center border border-blue-100">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <Brain className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Core Features Coming Soon
          </h2>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            We're building the complete MindMirror experience with journaling forms, 
            AI chat companion, history view, and intelligent insights. 
            Stay tuned for the full application!
          </p>
        </div>

        {/* Debug Info */}
        <div className="mt-8 bg-gray-100 rounded-xl p-4">
          <h3 className="font-semibold text-gray-700 mb-2">Debug Information</h3>
          <div className="text-sm text-gray-600 space-y-1">
            <div>User ID: {user.id}</div>
            <div>Email: {user.email}</div>
            <div>Email Confirmed: {user.email_confirmed_at ? 'Yes' : 'No'}</div>
            <div>Session: {session ? 'Active' : 'None'}</div>
          </div>
        </div>
      </main>
    </div>
  )
} 