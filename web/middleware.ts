import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Allow everything in demo mode (local development)
  if (process.env.NEXT_PUBLIC_APP_MODE === 'demo') {
    return NextResponse.next()
  }

  // In production, only allow landing page and essential assets
  const allowedPaths = [
    '/landing',
    '/_next',
    '/favicon.ico',
    '/api/health', // Keep health endpoint for monitoring
    // Add any other static assets you need
    '/images',
    '/icons'
  ]

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
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
} 