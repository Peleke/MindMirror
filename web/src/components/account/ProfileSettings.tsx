'use client'

import { useAuth } from '../../../lib/auth-context'
import { createClient } from '../../../lib/supabase/client'
import { useRouter } from 'next/navigation'
import { Settings, User, LogOut, BrainCircuit } from 'lucide-react'
import { TraditionSelector } from '../dashboard/TraditionSelector'

export function ProfileSettings() {
  const { user } = useAuth()
  const router = useRouter()
  const supabase = createClient()

  const handleLogout = async () => {
    await supabase.auth.signOut()
    router.push('/login')
  }

  if (!user) {
    return null // Or a loading spinner
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Settings className="w-8 h-8 text-gray-500" />
          <h1 className="text-3xl font-bold text-gray-900">Profile & Settings</h1>
        </div>
        <p className="text-gray-600">
          Manage your account details and application preferences.
        </p>
      </div>

      <div className="space-y-8">
        {/* Account Information */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <User className="w-5 h-5 text-gray-700" />
            <h3 className="text-lg font-semibold text-gray-900">Account Information</h3>
          </div>
          <div className="text-sm text-gray-800 bg-gray-50 p-4 rounded-lg">
            <strong>Email:</strong> {user.email}
          </div>
        </div>

        {/* Tradition Selection */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <BrainCircuit className="w-5 h-5 text-indigo-700" />
            <h3 className="text-lg font-semibold text-gray-900">AI Tradition</h3>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Select the knowledge base your AI Companion and tools will use for providing insights and generating content.
          </p>
          <TraditionSelector />
        </div>
        
        {/* Logout */}
        <div className="bg-white rounded-2xl p-6 border border-red-200 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <LogOut className="w-5 h-5 text-red-700" />
            <h3 className="text-lg font-semibold text-gray-900">Logout</h3>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            You will be returned to the login page.
          </p>
          <button
            onClick={handleLogout}
            className="w-full py-2 px-4 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors"
          >
            Sign Out
          </button>
        </div>
      </div>
    </div>
  )
} 