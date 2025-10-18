import { NextRequest, NextResponse } from 'next/server'
import { createServiceRoleClient, createClient } from '../../../../../lib/supabase/server'

function generateCode(length = 8) {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  let code = ''
  for (let i = 0; i < length; i++) code += chars[Math.floor(Math.random() * chars.length)]
  return code
}

async function validateProgramExists(programId: string, accessToken: string): Promise<boolean> {
  try {
    // Query GraphQL gateway with user's auth token
    // Use the Docker service name 'gateway' instead of localhost when running in containers
    const gatewayUrl = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://gateway:4000/graphql'

    const query = `
      query GetProgram($id: ID!) {
        program(id: $id) {
          id_
          name
        }
      }
    `

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    }

    console.log('🔍 Validating program via GraphQL:', { gatewayUrl, programId, hasToken: !!accessToken })

    const response = await fetch(gatewayUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        query,
        variables: { id: programId }
      })
    })

    const result = await response.json()
    console.log('📊 GraphQL response:', JSON.stringify(result, null, 2))

    // Check if program exists
    if (result.errors) {
      console.error('GraphQL errors:', result.errors)
      return false
    }

    return !!result.data?.program
  } catch (error) {
    console.error('Failed to validate program:', error)
    return false
  }
}

export async function POST(req: NextRequest) {
  const supabase = await createClient()
  const serviceRoleSupabase = createServiceRoleClient()

  try {
    // Get the logged-in user's session
    const { data: { session }, error: sessionError } = await supabase.auth.getSession()

    if (sessionError || !session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await req.json().catch(() => ({})) as any
    const email = (body.email || '').toLowerCase().trim()
    const programId = (body.programId || '').trim()
    const expirationDate = body.expirationDate || null

    // Validation
    if (!email) {
      return NextResponse.json({ error: 'Email is required' }, { status: 400 })
    }

    if (!programId) {
      return NextResponse.json({ error: 'Program ID is required' }, { status: 400 })
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return NextResponse.json({ error: 'Invalid email format' }, { status: 400 })
    }

    // Validate program ID format (UUID)
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
    if (!uuidRegex.test(programId)) {
      return NextResponse.json({ error: 'Invalid program ID format (must be UUID)' }, { status: 400 })
    }

    // Validate program exists via GraphQL gateway using user's token
    const programExists = await validateProgramExists(programId, session.access_token)
    if (!programExists) {
      return NextResponse.json({
        error: 'Program not found. Please verify the program ID is correct.'
      }, { status: 404 })
    }

    // Check for existing unused voucher for this email (use service role for DB access)
    const { data: existing } = await serviceRoleSupabase
      .schema('waitlist')
      .from('vouchers')
      .select('code')
      .eq('assigned_email', email)
      .eq('status', 'unused')
      .single()

    if (existing) {
      return NextResponse.json({
        error: `Unused voucher already exists for this email (code: ${existing.code})`
      }, { status: 409 })
    }

    // Generate unique code
    const code = generateCode(8)

    // Create voucher with program_id stored in metadata (use service role for DB access)
    const { data: voucher, error: voucherError } = await serviceRoleSupabase
      .schema('waitlist')
      .from('vouchers')
      .insert({
        code,
        campaign: 'mindmirror', // Default campaign
        assigned_email: email,
        status: 'unused',
        expires_at: expirationDate || null,
        metadata: { program_id: programId } // Store program_id in metadata
      })
      .select()
      .single()

    if (voucherError) {
      console.error('Voucher creation error:', voucherError)
      return NextResponse.json({
        error: 'Failed to create voucher: ' + voucherError.message
      }, { status: 500 })
    }

    // Generate magic link
    const appSignupUrl = process.env.NEXT_PUBLIC_APP_SIGNUP_URL || 'http://localhost:8081/signup'
    const magicLink = `${appSignupUrl}?voucher=${encodeURIComponent(code)}`

    return NextResponse.json({
      magicLink,
      voucherId: voucher.id,
      code: voucher.code
    })

  } catch (error) {
    console.error('Magic link creation error:', error)
    return NextResponse.json({
      error: error instanceof Error ? error.message : 'Internal server error'
    }, { status: 500 })
  }
}
