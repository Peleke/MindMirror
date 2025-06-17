'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '../../../lib/supabase/client'
import { Brain, Users, Mail, BarChart3, LogOut, Settings } from 'lucide-react'

interface AdminDashboardProps {
  user: {
    id: string
    email?: string
  }
}

export default function AdminDashboard({ user }: AdminDashboardProps) {
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const supabase = createClient()

  const handleLogout = async () => {
    setLoading(true)
    await supabase.auth.signOut()
    router.push('/admin/login')
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mr-3">
                <Brain className="h-5 w-5 text-white" />
              </div>
              <h1 className="text-xl font-semibold text-gray-900">MindMirror Admin</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {user.email}
              </span>
              <button
                onClick={handleLogout}
                disabled={loading}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-gray-500 bg-white hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
              >
                <LogOut className="h-4 w-4 mr-1" />
                {loading ? 'Signing out...' : 'Sign out'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Welcome Section */}
          <div className="bg-white overflow-hidden shadow rounded-lg mb-6">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-2">
                Welcome to MindMirror Admin
              </h2>
              <p className="text-gray-600">
                Manage your waitlist subscribers and track email engagement. 
                Part of the Swae OS ecosystem.
              </p>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-6">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Users className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Total Subscribers
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        -
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Mail className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Emails Sent
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        -
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <BarChart3 className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Open Rate
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        -
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Settings className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Status
                      </dt>
                      <dd className="text-lg font-medium text-green-600">
                        Active
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Quick Actions
              </h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
                  <div className="flex items-center">
                    <Users className="h-5 w-5 text-purple-500 mr-3" />
                    <span className="text-sm font-medium text-gray-900">
                      View Subscribers
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Manage waitlist subscribers
                  </p>
                </div>

                <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
                  <div className="flex items-center">
                    <BarChart3 className="h-5 w-5 text-purple-500 mr-3" />
                    <span className="text-sm font-medium text-gray-900">
                      Email Analytics
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Track engagement metrics
                  </p>
                </div>

                <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
                  <div className="flex items-center">
                    <Settings className="h-5 w-5 text-purple-500 mr-3" />
                    <span className="text-sm font-medium text-gray-900">
                      Settings
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Configure admin preferences
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
} 