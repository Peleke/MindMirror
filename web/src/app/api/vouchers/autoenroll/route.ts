import { NextRequest, NextResponse } from 'next/server'
import { createServiceRoleClient } from '../../../../../lib/supabase/server'
import { createClient } from '../../../../../lib/supabase/server'

export async function POST(req: NextRequest) {
  const supaUser = await createClient()
  const { data: { user } } = await supaUser.auth.getUser()
  if (!user) return NextResponse.json({ ok: true, enrolled: false })

  const supabase = createServiceRoleClient()
  const email = (user.email || '').toLowerCase()

  // Find unused voucher for this email
  const { data: v, error } = await supabase
    .schema('waitlist')
    .from('vouchers')
    .select('id, code, campaign, status, assigned_email')
    .eq('assigned_email', email)
    .eq('status', 'unused')
    .limit(1)
  if (error) return NextResponse.json({ ok: false, error: error.message }, { status: 500 })
  if (!v || v.length === 0) {
    // Check for cookie mismatch hint
    const cookieEmail = req.cookies.get('voucher_email')?.value
    if (cookieEmail && cookieEmail.toLowerCase() !== email) {
      return NextResponse.json({ ok: true, enrolled: false, reason: 'email_mismatch' })
    }
    return NextResponse.json({ ok: true, enrolled: false })
  }

  const voucher = v[0]
  // Insert enrollment
  const { data: enroll, error: enrollErr } = await supabase
    .schema('waitlist')
    .from('program_enrollments')
    .insert({ user_id: user.id, campaign: voucher.campaign, voucher_id: voucher.id, source: 'email', status: 'active' })
    .select('id')
    .single()
  if (enrollErr) return NextResponse.json({ ok: false, error: enrollErr.message }, { status: 500 })

  const { error: updErr } = await supabase
    .schema('waitlist')
    .from('vouchers')
    .update({ status: 'redeemed', redeemed_at: new Date().toISOString(), redeemed_by: user.id })
    .eq('id', voucher.id)
  if (updErr) return NextResponse.json({ ok: false, error: updErr.message }, { status: 500 })

  const res = NextResponse.json({ ok: true, enrolled: true, enrollmentId: enroll.id })
  res.cookies.delete('voucher_email')
  res.cookies.delete('voucher_campaign')
  return res
}


