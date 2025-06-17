'use client'

import { useEffect, useState } from 'react'
import { useQuery } from '@apollo/client'
import { useTradition } from '../../../lib/tradition-context'
import { LIST_TRADITIONS } from '../../../lib/graphql/queries'
import { ChevronDown, Book, Loader2, AlertCircle } from 'lucide-react'
import { cn } from '../../../lib/utils'

interface TraditionSelectorProps {
  className?: string
}

export function TraditionSelector({ className }: TraditionSelectorProps) {
  const { selectedTradition, setSelectedTradition, traditions, setTraditions } = useTradition()
  const [isOpen, setIsOpen] = useState(false)

  const { data, loading, error } = useQuery(LIST_TRADITIONS, {
    errorPolicy: 'all'
  })

  // Update traditions when data loads
  useEffect(() => {
    if (data?.listTraditions) {
      setTraditions(data.listTraditions)
    }
  }, [data, setTraditions])

  const handleTraditionSelect = (tradition: string) => {
    setSelectedTradition(tradition)
    setIsOpen(false)
  }

  // Format tradition name for display
  const formatTraditionName = (tradition: string) => {
    return tradition
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  if (loading) {
    return (
      <div className={cn('flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg', className)}>
        <Book className="w-4 h-4 text-gray-500" />
        <Loader2 className="w-4 h-4 text-gray-500 animate-spin" />
        <span className="text-sm text-gray-600">Loading traditions...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className={cn('flex items-center gap-2 px-3 py-2 bg-red-50 rounded-lg', className)}>
        <AlertCircle className="w-4 h-4 text-red-500" />
        <span className="text-sm text-red-600">Failed to load traditions</span>
      </div>
    )
  }

  return (
    <div className={cn('relative', className)}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <Book className="w-4 h-4 text-blue-600" />
        <span className="text-sm font-medium text-gray-700">
          {formatTraditionName(selectedTradition)}
        </span>
        <ChevronDown className={cn(
          'w-4 h-4 text-gray-400 transition-transform',
          isOpen && 'rotate-180'
        )} />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div className="absolute top-full left-0 mt-1 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-20">
            <div className="py-2">
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider border-b border-gray-100">
                Knowledge Base
              </div>
              {traditions.map((tradition) => (
                <button
                  key={tradition}
                  onClick={() => handleTraditionSelect(tradition)}
                  className={cn(
                    'w-full text-left px-3 py-2 text-sm hover:bg-gray-50 transition-colors',
                    selectedTradition === tradition && 'bg-blue-50 text-blue-700'
                  )}
                >
                  <div className="font-medium">
                    {formatTraditionName(tradition)}
                  </div>
                  <div className="text-xs text-gray-500">
                    {tradition === 'canon-default' 
                      ? 'Default knowledge base'
                      : `Custom tradition: ${tradition}`}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
} 