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
    const base = (process.env.NEXT_PUBLIC_BASE_URL && process.env.NEXT_PUBLIC_BASE_URL.replace(/\/$/, ''))
      || (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : '')
      || 'http://localhost:3000'
    const redeemUrl = `${base}/redeem?code=${encodeURIComponent(code)}`
    const html = `<p>Here is your voucher code: <b>${code}</b></p><p>Click to redeem: <a href="${redeemUrl}">${redeemUrl}</a></p>`
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${resendKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from, to: email, subject, html, text: `Your code: ${code}\nRedeem: ${redeemUrl}` })
    })
  } catch (_) {}

  return NextResponse.json({ ok: true })
}


