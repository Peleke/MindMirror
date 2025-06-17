import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export async function GET(request: NextRequest) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/dashboard'

  if (code) {
    const supabase = createClient(supabaseUrl, supabaseAnonKey)
    
    try {
      const { error } = await supabase.auth.exchangeCodeForSession(code)
      
      if (error) {
        console.error('Auth callback error:', error)
        return NextResponse.redirect(`${origin}/login?error=auth_callback_error`)
      }
      
      // Successful authentication
      return NextResponse.redirect(`${origin}${next}`)
    } catch (error) {
      console.error('Unexpected auth callback error:', error)
      return NextResponse.redirect(`${origin}/login?error=unexpected_error`)
    }
  }

  // No code provided
  return NextResponse.redirect(`${origin}/login?error=no_code_provided`)
} 