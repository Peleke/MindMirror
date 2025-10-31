import { NextRequest, NextResponse } from 'next/server'
import { createServiceRoleClient } from '../../../../../../lib/supabase/server'
import { createClient } from '../../../../../../lib/supabase/server'
import { isUserAdmin } from '../../../../../../lib/supabase/admin'

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => ({})) as any
  const code = (body.code || '').trim()
  const targetEmail = (body.email || '').toLowerCase()
  if (!code) return NextResponse.json({ error: 'code required' }, { status: 400 })

  // Verify admin session
  const supaUser = await createClient()
  const { data: { user } } = await supaUser.auth.getUser()
  if (!user) return NextResponse.json({ error: 'unauthorized' }, { status: 401 })
  const admin = await isUserAdmin(user.id)
  if (!admin) return NextResponse.json({ error: 'forbidden' }, { status: 403 })

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

  // Resolve user to redeem for
  let redeemUserId: string | null = null
  if (targetEmail) {
    const { data: urow, error: uerr } = await supabase
      .from('auth.users' as any)
      .select('id, email')
      .eq('email', targetEmail)
      .single()
    if (uerr || !urow) return NextResponse.json({ error: 'user not found for email' }, { status: 400 })
    redeemUserId = (urow as any).id
  } else {
    if (!user) return NextResponse.json({ error: 'unauthorized' }, { status: 401 })
    redeemUserId = user.id
  }

  // Admin flow: ignore assigned_email mismatch, but record enrollment
  const { data: enroll, error: enrollErr } = await supabase
    .schema('waitlist')
    .from('program_enrollments')
    .insert({ user_id: redeemUserId, campaign: voucher.campaign, voucher_id: voucher.id, source: 'email', status: 'active' })
    .select('id')
    .single()
  if (enrollErr) return NextResponse.json({ error: enrollErr.message }, { status: 500 })

  const { error: updErr } = await supabase
    .schema('waitlist')
    .from('vouchers')
    .update({ status: 'redeemed', redeemed_at: new Date().toISOString(), redeemed_by: redeemUserId })
    .eq('id', voucher.id)
  if (updErr) return NextResponse.json({ error: updErr.message }, { status: 500 })

  return NextResponse.json({ ok: true, enrollmentId: enroll.id })
}


