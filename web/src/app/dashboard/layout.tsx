'use client'

import { Sidebar } from '../../components/dashboard/Sidebar'
import { Header } from '../../components/dashboard/Header'
import { MobileNav } from '../../components/dashboard/MobileNav'
import { ApolloProviderWrapper } from '../../../lib/apollo-provider'
import { TraditionProvider } from '../../../lib/tradition-context'

interface DashboardLayoutProps {
  children: React.ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <TraditionProvider>
      <ApolloProviderWrapper>
        <div className="min-h-screen bg-gray-50 flex">
          {/* Desktop Sidebar */}
          <div className="hidden md:flex">
            <Sidebar />
          </div>

          {/* Main Content Area */}
          <div className="flex-1 flex flex-col min-w-0">
            {/* Header with Mobile Nav */}
            <div className="relative">
              <Header />
              {/* Mobile nav button positioned in header */}
              <div className="absolute left-4 top-1/2 -translate-y-1/2 md:hidden">
                <MobileNav />
              </div>
            </div>

            {/* Page Content */}
            <main className="flex-1 overflow-auto">
              <div className="h-full">
                {children}
              </div>
            </main>
          </div>
        </div>
      </ApolloProviderWrapper>
    </TraditionProvider>
  )
} 