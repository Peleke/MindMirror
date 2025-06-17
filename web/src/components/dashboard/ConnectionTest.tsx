'use client'

import { useState } from 'react'
import { useQuery } from '@apollo/client'
import { LIST_TRADITIONS } from '../../../lib/graphql/queries'
import { apolloConfig } from '../../../lib/apollo-client'
import { useAuth } from '../../../lib/auth-context'
import { CheckCircle, XCircle, Loader2, Wifi, WifiOff, AlertTriangle } from 'lucide-react'

export function ConnectionTest() {
  const { session, user } = useAuth()
  const [testConnection, setTestConnection] = useState(false)

  const { data, loading, error, refetch } = useQuery(LIST_TRADITIONS, {
    skip: !testConnection, // Only run when we explicitly test
    errorPolicy: 'all',
    fetchPolicy: 'network-only' // Always fetch fresh for testing
  })

  const handleTestConnection = () => {
    setTestConnection(true)
    refetch()
  }

  const getConnectionStatus = () => {
    if (!testConnection) return 'idle'
    if (loading) return 'testing'
    if (error) return 'error'
    if (data) return 'success'
    return 'unknown'
  }

  const status = getConnectionStatus()

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
      <div className="flex items-center gap-3 mb-4">
        {status === 'success' && <CheckCircle className="w-8 h-8 text-green-600" />}
        {status === 'error' && <XCircle className="w-8 h-8 text-red-600" />}
        {status === 'testing' && <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />}
        {status === 'idle' && <Wifi className="w-8 h-8 text-gray-400" />}
        <h3 className="text-lg font-semibold text-gray-900">Gateway Connection</h3>
      </div>

      <div className="space-y-3 text-sm mb-4">
        <div className="flex justify-between">
          <span className="text-gray-600">Gateway URL:</span>
          <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded">
            {apolloConfig.gatewayUrl}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Environment:</span>
          <span className="font-medium">
            {apolloConfig.isDocker ? 'Docker' : 'Local'}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">User ID:</span>
          <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded truncate max-w-32">
            {user?.id || 'None'}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">JWT Token:</span>
          <span className="font-medium">
            {session?.access_token ? '✅ Present' : '❌ Missing'}
          </span>
        </div>
      </div>

      {/* Status Messages */}
      {status === 'success' && (
        <div className="flex items-center gap-2 p-3 bg-green-50 text-green-700 rounded-lg mb-4">
          <CheckCircle className="w-5 h-5" />
          <div>
            <div className="font-medium">Connection Successful!</div>
            <div className="text-sm">
              Loaded {data?.listTraditions?.length || 0} traditions from Gateway
            </div>
          </div>
        </div>
      )}

      {status === 'error' && (
        <div className="flex items-start gap-2 p-3 bg-red-50 text-red-700 rounded-lg mb-4">
          <XCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <div className="font-medium">Connection Failed</div>
            <div className="text-sm mt-1">
              {error?.networkError ? (
                <>Network Error: {error.networkError.message}</>
              ) : error?.graphQLErrors?.length ? (
                <>GraphQL Error: {error.graphQLErrors[0].message}</>
              ) : (
                <>Unknown error occurred</>
              )}
            </div>
            {error?.networkError && (
              <div className="text-xs mt-2 font-mono bg-red-100 p-2 rounded">
                Check if Gateway is running at {apolloConfig.gatewayUrl}
              </div>
            )}
          </div>
        </div>
      )}

      {status === 'testing' && (
        <div className="flex items-center gap-2 p-3 bg-blue-50 text-blue-700 rounded-lg mb-4">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span className="font-medium">Testing connection to Gateway...</span>
        </div>
      )}

      {/* Test Button */}
      <button
        onClick={handleTestConnection}
        disabled={loading}
        className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'Testing...' : 'Test Gateway Connection'}
      </button>

      {/* Debug Info */}
      {data && (
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <div className="text-xs font-semibold text-gray-700 mb-2">Response Data:</div>
          <pre className="text-xs text-gray-600 overflow-x-auto">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
} 