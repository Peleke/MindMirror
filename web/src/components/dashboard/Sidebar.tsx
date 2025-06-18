'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Brain, 
  Heart, 
  Lightbulb, 
  PenTool, 
  History, 
  MessageCircle, 
  Upload, 
  Settings, 
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  FileText,
  Utensils,
  FileUp,
  MessageSquare
} from 'lucide-react'
import { cn } from '../../../lib/utils'

interface SidebarProps {
  className?: string
}

const navigationItems = [
  {
    title: 'Home',
    items: [
      {
        name: 'Dashboard',
        href: '/dashboard',
        icon: LayoutDashboard,
        description: 'Your central hub'
      }
    ]
  },
  {
    title: 'Daily Routine',
    items: [
      {
        name: 'Morning Gratitude',
        href: '/dashboard/gratitude',
        icon: Heart,
        description: 'Start your day with gratitude'
      },
      {
        name: 'Evening Reflection',
        href: '/dashboard/reflection',
        icon: Lightbulb,
        description: 'Reflect on your day'
      }
    ]
  },
  {
    title: 'Journaling',
    items: [
      {
        name: 'Freeform Journal',
        href: '/dashboard/journal',
        icon: PenTool,
        description: 'Write freely about anything'
      },
      {
        name: 'Journal History',
        href: '/dashboard/history',
        icon: History,
        description: 'View your past entries'
      }
    ]
  },
  {
    title: 'AI Companion',
    items: [
      {
        name: 'Chat',
        href: '/dashboard/chat',
        icon: MessageCircle,
        description: 'Talk with your AI companion'
      },
    ]
  },
  {
    title: 'Tools',
    items: [
      {
        name: 'Document Upload',
        href: '/dashboard/uploads',
        icon: Upload,
        description: 'Upload PDFs and text files',
        disabled: true,
        badge: 'Soon'
      },
      {
        name: 'Bi-Weekly Review',
        href: '/dashboard/review',
        icon: FileText,
        description: 'Generate performance insights'
      }
    ]
  },
  {
    title: 'Account',
    items: [
      {
        name: 'Profile & Settings',
        href: '/dashboard/settings',
        icon: Settings,
        description: 'Manage your account'
      }
    ]
  }
]

export function Sidebar({ className }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const pathname = usePathname()

  return (
    <div className={cn(
      'flex flex-col bg-white border-r border-gray-200 transition-all duration-300',
      isCollapsed ? 'w-16' : 'w-64',
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <Link href="/dashboard" className="flex items-center gap-3" title="Go to Dashboard">
          {!isCollapsed && (
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center shadow-md">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <span className="text-lg font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                  MindMirror
                </span>
              </div>
          )}
           {isCollapsed && (
             <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center shadow-md">
               <Brain className="w-5 h-5 text-white" />
             </div>
           )}
        </Link>
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
        >
          {isCollapsed ? (
            <ChevronRight className="w-4 h-4 text-gray-600" />
          ) : (
            <ChevronLeft className="w-4 h-4 text-gray-600" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        <div className="space-y-6">
          {navigationItems.map((section) => (
            <div key={section.title}>
              {!isCollapsed && (
                <div className="px-4 mb-2">
                  <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    {section.title}
                  </h3>
                </div>
              )}
              <div className="space-y-1">
                {section.items.map((item) => {
                  const Icon = item.icon
                  const isActive = pathname === item.href
                  
                  return (
                    <Link
                      key={item.href}
                      href={item.disabled ? '#' : item.href}
                      className={cn(
                        'flex items-center gap-3 px-4 py-2.5 text-sm font-medium transition-colors relative group',
                        isActive && !item.disabled
                          ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                          : 'text-gray-700',
                        !item.disabled && 'hover:bg-gray-50 hover:text-gray-900',
                        item.disabled && 'opacity-50 cursor-not-allowed'
                      )}
                      title={isCollapsed ? item.name : undefined}
                      onClick={(e) => item.disabled && e.preventDefault()}
                    >
                      <Icon className={cn(
                        'w-5 h-5 flex-shrink-0',
                        isActive && !item.disabled ? 'text-blue-600' : 'text-gray-500'
                      )} />
                      {!isCollapsed && (
                        <div className="flex-1 min-w-0 flex justify-between items-center">
                          <div>
                            <div className="font-medium">{item.name}</div>
                            <div className="text-xs text-gray-500 truncate">
                              {item.description}
                            </div>
                          </div>
                          {item.badge && (
                            <span className="bg-gray-200 text-gray-600 text-xs font-medium px-2 py-0.5 rounded-full">
                              {item.badge}
                            </span>
                          )}
                        </div>
                      )}
                      
                      {/* Tooltip for collapsed state */}
                      {isCollapsed && (
                        <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50">
                          {item.name}
                        </div>
                      )}
                    </Link>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      </nav>
    </div>
  )
}

function NavItem({ href, icon: Icon, label, disabled = false, children }: { href: string; icon: any; label: string; disabled?: boolean; children?: React.ReactNode }) {
  const pathname = usePathname()
  const isActive = pathname === href

  const linkClasses = cn(
    "flex items-center gap-3 rounded-lg px-3 py-2 text-gray-600 transition-all",
    isActive && "bg-gray-100 text-gray-900 font-semibold",
    !disabled && "hover:bg-gray-100 hover:text-gray-900",
    disabled && "cursor-not-allowed opacity-50"
  );

  const linkContent = (
    <>
      <Icon className="h-4 w-4" />
      <span className="flex-1">{label}</span>
      {children}
    </>
  );

  if (disabled) {
    return (
      <li>
        <span className={linkClasses}>
          {linkContent}
        </span>
      </li>
    );
  }

  return (
    <li>
      <Link href={href} className={linkClasses}>
        {linkContent}
      </Link>
    </li>
  );
} 