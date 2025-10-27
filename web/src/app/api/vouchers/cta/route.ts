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
  return `${resolveWebBaseUrl()}/mindmirror-mobile/signup`
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
    const appSignup = (searchParams.get('redirect') || resolveAppSignupUrl()).replace(/\/$/, '')
    const redeemUrl = `${base}/redeem?code=${encodeURIComponent(code)}`
    const programName = campaign === 'uye' ? 'Unf*ck Your Eating' : 'MindMirror'
    const subject = `Your ${campaign.toUpperCase()} voucher`
    const html = `
    <div style="width:100%;">
      <div style="max-width:560px;margin:0 auto;padding:16px 16px 0 16px">
        <p style=\"font-size:14px;color:#111827;margin:0 0 12px 0\">🎉 We're glad you're here — and your access is ready! 🎉</p>
        <p style=\"font-size:14px;color:#374151;margin:0 0 8px 0\">To take advantage of your free access:</p>
        <ul style=\"margin:0 0 12px 20px;padding:0;color:#374151;font-size:14px;line-height:20px\">
          <li>Click here to create your account: <a href=\"${appSignup}\">${appSignup}</a></li>
          <li>Use the same email this message was sent to: <b>${email}</b></li>
        </ul>
        <p style=\"font-size:14px;color:#374151;margin:0 0 6px 0\">Here’s your voucher code: <b>${code}</b></p>
        <p style=\"font-size:12px;color:#6b7280;margin:0 0 12px 0\">You’ll only need it if the app asks — if you sign up with <b>${email}</b>, you’ll be enrolled automatically. Otherwise, you can enter it manually in the app (Marketplace → Redeem Voucher).</p>
        <p style=\"font-size:12px;color:#6b7280;margin:0 0 24px 0\">Already enrolled in ${programName}? You can safely ignore this email.</p>
      </div>
    </div>`
    const text = `We're glad you're here!\n\nTo take advantage of your free access:\n- Create your account: ${appSignup}\n- Use the same email this message was sent to: ${email}\n\nYour voucher code: ${code}\n(Only needed if the app asks. If you sign up with ${email}, you’ll be enrolled automatically.)\n\nAlready enrolled in ${programName}? You can ignore this email.`
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${resendKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from, to: email, subject, html, text })
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


