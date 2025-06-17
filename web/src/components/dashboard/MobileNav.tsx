'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Menu, 
  X, 
  Brain,
  Heart, 
  Lightbulb, 
  PenTool, 
  History, 
  MessageCircle, 
  Upload, 
  Settings,
  FileText,
  Utensils
} from 'lucide-react'
import { cn } from '../../../lib/utils'

interface MobileNavProps {
  className?: string
}

const navigationItems = [
  {
    name: 'Morning Gratitude',
    href: '/dashboard/gratitude',
    icon: Heart,
  },
  {
    name: 'Evening Reflection',
    href: '/dashboard/reflection',
    icon: Lightbulb,
  },
  {
    name: 'Freeform Journal',
    href: '/dashboard/journal',
    icon: PenTool,
  },
  {
    name: 'Journal History',
    href: '/dashboard/history',
    icon: History,
  },
  {
    name: 'AI Chat',
    href: '/dashboard/chat',
    icon: MessageCircle,
  },
  {
    name: 'Meal Suggestions',
    href: '/dashboard/meals',
    icon: Utensils,
  },
  {
    name: 'Document Upload',
    href: '/dashboard/uploads',
    icon: Upload,
  },
  {
    name: 'Bi-Weekly Review',
    href: '/dashboard/review',
    icon: FileText,
  },
  {
    name: 'Settings',
    href: '/dashboard/settings',
    icon: Settings,
  }
]

export function MobileNav({ className }: MobileNavProps) {
  const [isOpen, setIsOpen] = useState(false)
  const pathname = usePathname()

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(true)}
        className={cn(
          'md:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors',
          className
        )}
      >
        <Menu className="w-6 h-6" />
      </button>

      {/* Mobile menu overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          {/* Backdrop */}
          <div 
            className="fixed inset-0 bg-black bg-opacity-50" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Menu panel */}
          <div className="fixed inset-y-0 left-0 w-80 max-w-[80vw] bg-white shadow-xl">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center shadow-md">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <span className="text-lg font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                  MindMirror
                </span>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto py-4">
              <div className="space-y-1">
                {navigationItems.map((item) => {
                  const Icon = item.icon
                  const isActive = pathname === item.href
                  
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setIsOpen(false)}
                      className={cn(
                        'flex items-center gap-3 px-4 py-3 text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-blue-50 text-blue-700 border-r-4 border-blue-600'
                          : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                      )}
                    >
                      <Icon className={cn(
                        'w-5 h-5 flex-shrink-0',
                        isActive ? 'text-blue-600' : 'text-gray-500'
                      )} />
                      <span>{item.name}</span>
                    </Link>
                  )
                })}
              </div>
            </nav>
          </div>
        </div>
      )}
    </>
  )
} 