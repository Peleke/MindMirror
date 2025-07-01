'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface TraditionContextType {
  selectedTradition: string
  setSelectedTradition: (tradition: string) => void
  traditions: string[]
  setTraditions: (traditions: string[]) => void
  loading: boolean
  setLoading: (loading: boolean) => void
}

const TraditionContext = createContext<TraditionContextType | undefined>(undefined)

const DEFAULT_TRADITION = 'canon-default'
const TRADITION_STORAGE_KEY = 'mindmirror-selected-tradition'

interface TraditionProviderProps {
  children: ReactNode
}

export function TraditionProvider({ children }: TraditionProviderProps) {
  const [selectedTradition, setSelectedTraditionState] = useState<string>(DEFAULT_TRADITION)
  const [traditions, setTraditions] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  // Load selected tradition from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(TRADITION_STORAGE_KEY)
    console.log('TraditionProvider: localStorage value =', stored)
    if (stored) {
      // Fix legacy 'default' value to 'canon-default'
      const tradition = stored === 'default' ? 'canon-default' : stored
      console.log('TraditionProvider: Setting selectedTradition to stored value:', tradition)
      setSelectedTraditionState(tradition)
      // Update localStorage if we fixed the value
      if (tradition !== stored) {
        localStorage.setItem(TRADITION_STORAGE_KEY, tradition)
      }
    } else {
      console.log('TraditionProvider: No stored value, using default:', DEFAULT_TRADITION)
    }
    setLoading(false)
  }, [])

  // Add logging whenever selectedTradition changes
  useEffect(() => {
    console.log('TraditionProvider: selectedTradition changed to:', selectedTradition)
  }, [selectedTradition])

  // Save selected tradition to localStorage when it changes
  const setSelectedTradition = (tradition: string) => {
    setSelectedTraditionState(tradition)
    localStorage.setItem(TRADITION_STORAGE_KEY, tradition)
  }

  const value: TraditionContextType = {
    selectedTradition,
    setSelectedTradition,
    traditions,
    setTraditions,
    loading,
    setLoading
  }

  return (
    <TraditionContext.Provider value={value}>
      {children}
    </TraditionContext.Provider>
  )
}

export function useTradition() {
  const context = useContext(TraditionContext)
  if (context === undefined) {
    throw new Error('useTradition must be used within a TraditionProvider')
  }
  return context
} 