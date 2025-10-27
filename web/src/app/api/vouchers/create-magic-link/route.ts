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
    const result = await validateProgramExistsWithDetails(programId, accessToken)
    return !!result
  } catch (error) {
    console.error('Failed to validate program:', error)
    return false
  }
}

async function validateProgramExistsWithDetails(programId: string, accessToken: string): Promise<{ id_: string; name: string } | null> {
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
      return null
    }

    return result.data?.program || null
  } catch (error) {
    console.error('Failed to validate program:', error)
    return null
  }
}

async function sendMagicLinkEmail(params: {
  toEmail: string
  magicLink: string
  code: string
  programName: string
  personalMessage: string | null
}): Promise<void> {
  const { toEmail, magicLink, code, programName, personalMessage } = params

  const resendKey = process.env.RESEND_API_KEY
  if (!resendKey) {
    throw new Error('RESEND_API_KEY not configured')
  }

  const from = 'mindmirror@emails.peleke.me'
  const subject = `Your MindMirror Invitation - ${programName}`

  // Default message if no personal message provided
  const defaultMessage = `You've been invited to join MindMirror and start your journey with ${programName}.`

  const html = `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
      <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #7c3aed; margin: 0; font-size: 28px;">MindMirror</h1>
        <p style="color: #6b7280; margin: 5px 0 0 0; font-size: 14px;">Your Personal Performance Platform</p>
      </div>

      <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 30px; margin-bottom: 30px;">
        <h2 style="color: white; margin: 0 0 15px 0; font-size: 24px;">You're Invited! 🎉</h2>
        <p style="color: #e0e7ff; margin: 0; font-size: 16px; line-height: 1.6;">
          ${personalMessage || defaultMessage}
        </p>
      </div>

      <div style="background: #f9fafb; border-radius: 8px; padding: 25px; margin-bottom: 25px;">
        <h3 style="margin: 0 0 15px 0; color: #111827; font-size: 18px;">Your Program</h3>
        <div style="background: white; border-left: 4px solid #7c3aed; padding: 15px; border-radius: 4px;">
          <p style="margin: 0; color: #374151; font-size: 16px; font-weight: 600;">${programName}</p>
        </div>
      </div>

      <div style="text-align: center; margin-bottom: 30px;">
        <a href="${magicLink}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; padding: 16px 40px; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
          Get Started with MindMirror
        </a>
      </div>

      <div style="background: #fef3c7; border: 1px solid #fde68a; border-radius: 8px; padding: 15px; margin-bottom: 25px;">
        <p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.6;">
          <strong>Your Access Code:</strong> <code style="background: white; padding: 2px 6px; border-radius: 4px; font-family: monospace;">${code}</code><br/>
          You'll only need this if the app asks for it during signup.
        </p>
      </div>

      <div style="border-top: 1px solid #e5e7eb; padding-top: 20px; margin-top: 30px;">
        <p style="color: #6b7280; font-size: 14px; margin: 0 0 10px 0;">
          <strong>Can't click the button?</strong> Copy and paste this link into your browser:
        </p>
        <p style="margin: 0;">
          <a href="${magicLink}" style="color: #7c3aed; font-size: 13px; word-break: break-all;">${magicLink}</a>
        </p>
      </div>

      <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
        <p style="color: #9ca3af; font-size: 12px; margin: 0;">
          Part of the Swae OS ecosystem
        </p>
      </div>
    </div>
  `

  const text = `
You're Invited to MindMirror!

${personalMessage || defaultMessage}

Your Program: ${programName}

Get started by clicking this link:
${magicLink}

Your Access Code: ${code}
(You'll only need this if the app asks for it during signup)

Can't click the link? Copy and paste it into your browser.

---
Part of the Swae OS ecosystem
  `.trim()

  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${resendKey}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      from,
      to: toEmail,
      subject,
      html,
      text
    })
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(`Resend API error: ${JSON.stringify(errorData)}`)
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
    const personalMessage = body.personalMessage || null
    const sendEmail = body.sendEmail !== undefined ? body.sendEmail : true

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

    // Get program name for email
    let programName = 'your workout program'
    try {
      const programResult = await validateProgramExistsWithDetails(programId, session.access_token)
      if (programResult) {
        programName = programResult.name
      }
    } catch (err) {
      console.error('Failed to get program name:', err)
    }

    // Send email if requested
    let emailSent = false
    if (sendEmail) {
      try {
        await sendMagicLinkEmail({
          toEmail: email,
          magicLink,
          code,
          programName,
          personalMessage
        })
        emailSent = true
        console.log('✅ Magic link email sent to:', email)
      } catch (emailError) {
        console.error('Failed to send email:', emailError)
        // Don't fail the whole request if email fails, just log it
      }
    }

    return NextResponse.json({
      magicLink,
      voucherId: voucher.id,
      code: voucher.code,
      emailSent,
      programName
    })

  } catch (error) {
    console.error('Magic link creation error:', error)
    return NextResponse.json({
      error: error instanceof Error ? error.message : 'Internal server error'
    }, { status: 500 })
  }
}
