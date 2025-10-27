import { NextRequest, NextResponse } from 'next/server'
import { createServiceRoleClient } from '../../../../../lib/supabase/server'

function generateCode(length = 10) {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  let code = ''
  for (let i = 0; i < length; i++) code += chars[Math.floor(Math.random() * chars.length)]
  return code
}

export async function POST(req: NextRequest) {
  const supabase = createServiceRoleClient()
  const body = await req.json().catch(() => ({})) as any
  const email = (body.email || '').toLowerCase()
  const campaign = (body.campaign || 'uye').toLowerCase()
  if (!email) return NextResponse.json({ error: 'email required' }, { status: 400 })

  // Create voucher
  const code = generateCode(8)
  const { data: v, error } = await supabase
    .schema('waitlist')
    .from('vouchers')
    .insert({ code, campaign, assigned_email: email, status: 'unused' })
    .select()
    .single()
  if (error) return NextResponse.json({ error: error.message }, { status: 500 })

  // Send email via Resend (simple JSON fetch)
  try {
    const resendKey = process.env.RESEND_API_KEY
    const from = campaign === 'uye' ? 'uye@emails.peleke.me' : 'mindmirror@emails.peleke.me'
    const subject = `Your ${campaign.toUpperCase()} voucher`
    const webBase = (process.env.NEXT_PUBLIC_BASE_URL && process.env.NEXT_PUBLIC_BASE_URL.replace(/\/$/, ''))
      || (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : '')
      || 'http://localhost:3000'
    const appSignupUrl = (process.env.NEXT_PUBLIC_APP_SIGNUP_URL && process.env.NEXT_PUBLIC_APP_SIGNUP_URL.replace(/\/$/, ''))
      || (process.env.EMAIL_APP_SIGNUP_URL && process.env.EMAIL_APP_SIGNUP_URL.replace(/\/$/, ''))
      || 'http://localhost:8081/signup'
    const redeemUrl = `${webBase}/redeem?code=${encodeURIComponent(code)}`
    const programName = campaign === 'uye' ? 'Unf*ck Your Eating' : 'MindMirror'
    const html = `
    <div style="width:100%;">
      <div style="max-width:560px;margin:0 auto;padding:16px 16px 0 16px">
        <p style="font-size:14px;color:#111827;margin:0 0 12px 0">🎉 We're glad you're here — and your access is ready! 🎉</p>
        <p style="font-size:14px;color:#374151;margin:0 0 8px 0">To take advantage of your free access:</p>
        <ul style="margin:0 0 12px 20px;padding:0;color:#374151;font-size:14px;line-height:20px">
          <li>Click here to create your account: <a href="${appSignupUrl}">${appSignupUrl}</a></li>
          <li>Use the same email this message was sent to: <b>${email}</b></li>
        </ul>
        <p style="font-size:14px;color:#374151;margin:0 0 6px 0">Here’s your voucher code: <b>${code}</b></p>
        <p style="font-size:12px;color:#6b7280;margin:0 0 12px 0">You’ll only need it if the app asks — if you sign up with <b>${email}</b>, you’ll be enrolled automatically. Otherwise, you can enter it manually in the app (Marketplace → Redeem Voucher).</p>
        <p style="font-size:12px;color:#6b7280;margin:0 0 12px 0">Already enrolled in ${programName}? You can safely ignore this email.</p>
        <p style="font-size:12px;color:#9ca3af;margin:0 0 24px 0">Manual fallback: <a href="${redeemUrl}">${redeemUrl}</a></p>
      </div>
    </div>`
    const text = `We're glad you're here!

To take advantage of your free access:
- Create your account: ${appSignupUrl}
- Use the same email this message was sent to: ${email}

Your voucher code: ${code}
(Only needed if the app asks. If you sign up with ${email}, you’ll be enrolled automatically.)

Already enrolled in ${programName}? You can ignore this email.
Manual fallback: ${redeemUrl}`
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${resendKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from, to: email, subject, html, text })
    })
  } catch (_) {}

  return NextResponse.json({ ok: true })
}


