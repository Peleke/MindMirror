import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '../../../../lib/supabase/server'

export async function POST(req: NextRequest) {
  const supabase = await createClient()

  try {
    // Get the logged-in user's session
    const { data: { session }, error: sessionError } = await supabase.auth.getSession()

    if (sessionError || !session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get the GraphQL query from request body
    const body = await req.json()

    // Forward to GraphQL gateway with user's auth token
    const gatewayUrl = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://gateway:4000/graphql'

    const response = await fetch(gatewayUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session.access_token}`
      },
      body: JSON.stringify(body)
    })

    const result = await response.json()

    return NextResponse.json(result)
  } catch (error) {
    console.error('GraphQL proxy error:', error)
    return NextResponse.json({
      errors: [{ message: 'Internal server error' }]
    }, { status: 500 })
  }
}
