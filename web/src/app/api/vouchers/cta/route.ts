import { NextRequest, NextResponse } from 'next/server'
import { createServiceRoleClient } from '../../../../../lib/supabase/server'

function resolveWebBaseUrl(): string {
  const vercel = process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : ''
  const pub = (process.env.NEXT_PUBLIC_BASE_URL || '').replace(/\/$/, '')
  return pub || vercel || 'http://localhost:3000'
}

function resolveAppSignupUrl(): string {
  // Prefer explicit app signup target (mobile preview or local device)
  const explicit = (process.env.NEXT_PUBLIC_APP_SIGNUP_URL || process.env.APP_SIGNUP_BASE_URL || '').replace(/\/$/, '')
  if (explicit) return explicit
  // Fallback to web root if not provided
  return resolveWebBaseUrl()
}

function generateCode(length = 8) {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  let code = ''
  for (let i = 0; i < length; i++) code += chars[Math.floor(Math.random() * chars.length)]
  return code
}

export async function GET(req: NextRequest) {
  const supabase = createServiceRoleClient()
  const { searchParams } = new URL(req.url)
  const email = (searchParams.get('email') || '').toLowerCase()
  const campaign = (searchParams.get('campaign') || 'uye').toLowerCase()
  if (!email) return NextResponse.redirect(`${resolveWebBaseUrl()}/landing`)

  // Create or reuse an unused voucher for this email+campaign
  let code = generateCode(8)
  const { data: existing } = await supabase
    .schema('waitlist')
    .from('vouchers')
    .select('id, code, status')
    .eq('assigned_email', email)
    .eq('campaign', campaign)
    .eq('status', 'unused')
    .limit(1)
  if (existing && existing.length > 0) code = existing[0].code
  else {
    const { error } = await supabase
      .schema('waitlist')
      .from('vouchers')
      .insert({ code, campaign, assigned_email: email, status: 'unused' })
    if (error) console.error('voucher insert error', error.message)
  }

  // Send voucher email
  try {
    const resendKey = process.env.RESEND_API_KEY
    const from = campaign === 'uye' ? 'uye@emails.peleke.me' : 'mindmirror@emails.peleke.me'
    const base = resolveWebBaseUrl()
    const redeemUrl = `${base}/redeem?code=${encodeURIComponent(code)}`
    const subject = `Your ${campaign.toUpperCase()} voucher`
    const html = `<p>We’re glad you’re here. Here’s your voucher code: <b>${code}</b></p><p><a href="${redeemUrl}">Click here to create your account</a>.</p><p>If you sign up with this email, you’ll be auto-enrolled. If anything goes wrong, use the code on the Marketplace → Redeem Voucher screen. If you’re already enrolled, feel free to ignore this email.</p>`
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${resendKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from, to: email, subject, html })
    })
  } catch (e) { console.error('voucher email error', e) }

  // Support redirect override via query param (?redirect=https://...)
  const redirectOverride = searchParams.get('redirect') || ''
  const target = (redirectOverride || resolveAppSignupUrl()) + '/'

  // Set short-lived cookies and redirect to signup/app root
  const res = NextResponse.redirect(target)
  res.cookies.set('voucher_email', email, { httpOnly: true, maxAge: 60 * 60 * 24, path: '/' })
  res.cookies.set('voucher_campaign', campaign, { httpOnly: true, maxAge: 60 * 60 * 24, path: '/' })
  return res
}


