'use client'

import { useAuth } from '../../../lib/auth-context'
import { useTradition } from '../../../lib/tradition-context'
import { LogOut, User, Globe, Server } from 'lucide-react'
import { TraditionSelector } from './TraditionSelector'
import { apolloConfig } from '../../../lib/apollo-client'

interface HeaderProps {
  className?: string
}

export function Header({ className }: HeaderProps) {
  const { user, signOut } = useAuth()
  const { selectedTradition } = useTradition()

  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('Error signing out:', error)
    }
  }

  return (
    <header className={`bg-white border-b border-gray-200 shadow-sm ${className || ''}`}>
      <div className="flex items-center justify-between h-16 px-6">
        {/* Left side - Environment indicator */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg">
            {apolloConfig.isDocker ? (
              <Server className="w-4 h-4 text-blue-600" />
            ) : (
              <Globe className="w-4 h-4 text-green-600" />
            )}
            <span className="text-sm font-medium text-gray-700">
              {apolloConfig.isDocker ? 'Docker' : 'Local'}
            </span>
          </div>
          
          {/* Tradition Selector */}
          <TraditionSelector />
        </div>

        {/* Right side - User menu */}
        <div className="flex items-center gap-4">
          {/* User info */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
            <div className="text-sm">
              <div className="font-medium text-gray-900">
                {user?.user_metadata?.full_name || 'User'}
              </div>
              <div className="text-gray-500">
                {user?.email}
              </div>
            </div>
          </div>

          {/* Logout button */}
          <button
            onClick={handleSignOut}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </div>
    </header>
  )
} 