'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '../../../lib/supabase/client'
import { Brain, Users, Mail, BarChart3, LogOut, Settings, Clock } from 'lucide-react'

interface AdminDashboardProps {
  user: {
    id: string
    email?: string
  }
}

interface DashboardStats {
  subscribers: {
    total: number
    active: number
    recentSignups: number
  }
  emails: {
    totalSent: number
    deliveryRate: number
    openRate: number
    clickRate: number
  }
}

interface Subscriber {
  id: number
  email: string
  subscribed_at: string
  source: string
  status: string
}

export default function AdminDashboard({ user }: AdminDashboardProps) {
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [subscribers, setSubscribers] = useState<Subscriber[]>([])
  const [showSubscribers, setShowSubscribers] = useState(false)
  const [loadingStats, setLoadingStats] = useState(true)
  const [loadingSubscribers, setLoadingSubscribers] = useState(false)
  const router = useRouter()
  const supabase = createClient()

  // Fetch dashboard stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/admin/stats')
        if (response.ok) {
          const data = await response.json()
          setStats(data)
        }
      } catch (error) {
        console.error('Error fetching stats:', error)
      } finally {
        setLoadingStats(false)
      }
    }

    fetchStats()
  }, [])

  // Fetch subscribers when needed
  const fetchSubscribers = async () => {
    if (subscribers.length > 0) return // Already loaded
    
    setLoadingSubscribers(true)
    try {
      const response = await fetch('/api/admin/subscribers')
      if (response.ok) {
        const data = await response.json()
        setSubscribers(data.subscribers)
      }
    } catch (error) {
      console.error('Error fetching subscribers:', error)
    } finally {
      setLoadingSubscribers(false)
    }
  }

  const handleViewSubscribers = () => {
    setShowSubscribers(true)
    fetchSubscribers()
  }

  const handleLogout = async () => {
    setLoading(true)
    await supabase.auth.signOut()
    router.push('/admin/login')
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
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
                        {loadingStats ? '...' : (stats?.subscribers.total || 0)}
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
                        {loadingStats ? '...' : (stats?.emails.totalSent || 0)}
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
                      <dd className="text-sm font-medium text-amber-600 flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        Coming Soon
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
          <div className="bg-white shadow rounded-lg mb-6">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Quick Actions
              </h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <button
                  onClick={handleViewSubscribers}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer text-left transition-colors"
                >
                  <div className="flex items-center">
                    <Users className="h-5 w-5 text-purple-500 mr-3" />
                    <span className="text-sm font-medium text-gray-900">
                      View Subscribers
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Manage waitlist subscribers
                  </p>
                </button>

                <a href="/admin/email" className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 block transition-colors">
                  <div className="flex items-center">
                    <Mail className="h-5 w-5 text-purple-500 mr-3" />
                    <span className="text-sm font-medium text-gray-900">
                      View Campaigns
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    See campaigns and subscriber positions
                  </p>
                </a>

                <a href="/admin/analytics" className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 block transition-colors">
                  <div className="flex items-center">
                    <BarChart3 className="h-5 w-5 text-purple-500 mr-3" />
                    <span className="text-sm font-medium text-gray-900">
                      Email Analytics
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    View engagement metrics
                  </p>
                </a>

                <a href="/admin/vouchers" className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 block transition-colors">
                  <div className="flex items-center">
                    <Mail className="h-5 w-5 text-purple-500 mr-3" />
                    <span className="text-sm font-medium text-gray-900">
                      Mint Voucher (test)
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Generate a voucher and email it to a tester
                  </p>
                </a>

                <div className="border border-gray-200 rounded-lg p-4 bg-gray-50 cursor-not-allowed">
                  <div className="flex items-center">
                    <Settings className="h-5 w-5 text-gray-400 mr-3" />
                    <span className="text-sm font-medium text-gray-500">
                      Settings
                    </span>
                    <Clock className="h-3 w-3 ml-2 text-amber-500" />
                  </div>
                  <p className="text-xs text-gray-400 mt-1">
                    Coming Soon - Configure admin preferences
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Subscribers Table */}
          {showSubscribers && (
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    Waitlist Subscribers
                  </h3>
                  <button
                    onClick={() => setShowSubscribers(false)}
                    className="text-sm text-gray-500 hover:text-gray-700"
                  >
                    Hide
                  </button>
                </div>
                
                {loadingSubscribers ? (
                  <div className="text-center py-8">
                    <div className="text-gray-500">Loading subscribers...</div>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Email
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Source
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Subscribed
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {subscribers.map((subscriber) => (
                          <tr key={subscriber.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {subscriber.email}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {subscriber.source}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                subscriber.status === 'active' 
                                  ? 'bg-green-100 text-green-800' 
                                  : 'bg-gray-100 text-gray-800'
                              }`}>
                                {subscriber.status}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {formatDate(subscriber.subscribed_at)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    
                    {subscribers.length === 0 && (
                      <div className="text-center py-8">
                        <div className="text-gray-500">No subscribers yet</div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
} 