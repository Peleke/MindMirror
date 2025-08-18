import { NextRequest, NextResponse } from 'next/server'
import { createServiceRoleClient } from '../../../../../lib/supabase/server'
import { createClient } from '../../../../../lib/supabase/server'

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => ({})) as any
  const code = (body.code || '').trim()
  if (!code) return NextResponse.json({ error: 'code required' }, { status: 400 })

  // Auth user
  const supaUser = await createClient()
  const { data: { user } } = await supaUser.auth.getUser()
  if (!user) return NextResponse.json({ error: 'unauthorized' }, { status: 401 })

  const supabase = createServiceRoleClient()
  // Fetch voucher
  const { data: voucher, error } = await supabase
    .schema('waitlist')
    .from('vouchers')
    .select('id, code, campaign, status, assigned_email, expires_at')
    .eq('code', code)
    .single()
  if (error || !voucher) return NextResponse.json({ error: 'invalid code' }, { status: 400 })
  if (voucher.status !== 'unused') return NextResponse.json({ error: 'already used or invalid' }, { status: 400 })
  if (voucher.expires_at && new Date(voucher.expires_at) < new Date()) return NextResponse.json({ error: 'expired' }, { status: 400 })
  if (voucher.assigned_email && voucher.assigned_email.toLowerCase() !== (user.email || '').toLowerCase()) {
    return NextResponse.json({ error: 'email mismatch' }, { status: 400 })
  }

  // Insert enrollment
  const { data: enroll, error: enrollErr } = await supabase
    .schema('waitlist')
    .from('program_enrollments')
    .insert({ user_id: user.id, campaign: voucher.campaign, voucher_id: voucher.id, source: 'email', status: 'active' })
    .select('id')
    .single()
  if (enrollErr) return NextResponse.json({ error: enrollErr.message }, { status: 500 })

  // Mark voucher redeemed
  const { error: updErr } = await supabase
    .schema('waitlist')
    .from('vouchers')
    .update({ status: 'redeemed', redeemed_at: new Date().toISOString(), redeemed_by: user.id })
    .eq('id', voucher.id)
  if (updErr) return NextResponse.json({ error: updErr.message }, { status: 500 })

  return NextResponse.json({ ok: true, enrollmentId: enroll.id })
}


