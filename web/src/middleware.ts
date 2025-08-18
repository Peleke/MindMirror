import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const appMode = process.env.NEXT_PUBLIC_APP_MODE || 'production'
  
  // Only allow full access in demo mode
  if (appMode === 'demo') {
    return NextResponse.next()
  }

  // In production mode, restrict to landing page only
  const allowedPaths = [
    '/landing',
    '/_next',
    '/favicon.ico',
    '/api/health', // Keep health endpoint for monitoring
    '/api/subscribe', // Allow subscribe API for landing page
    // Add any other static assets you need
    '/images',
    '/icons',
    // Admin routes (allow UI and API)
    '/admin',
    '/api/admin',
    // Resend webhook
    '/api/resend'
  ]

  // Special handling for root path - redirect to landing
  if (request.nextUrl.pathname === '/') {
    return NextResponse.redirect(new URL('/landing', request.url))
  }

  // Check if current path is allowed
  if (!allowedPaths.some(path => request.nextUrl.pathname.startsWith(path))) {
    // Redirect everything else to landing page
    return NextResponse.redirect(new URL('/landing', request.url))
  }

  // Add X-Robots-Tag header to prevent indexing non-landing routes in production
  const response = NextResponse.next()
  if (!request.nextUrl.pathname.startsWith('/landing')) {
    response.headers.set('X-Robots-Tag', 'noindex')
  }

  return response
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
} 