import { NextRequest, NextResponse } from 'next/server'
import { createServiceRoleClient } from '../../../../../lib/supabase/server'

export async function GET(req: NextRequest) {
  const supabase = createServiceRoleClient()
  const { searchParams } = new URL(req.url)
  const code = (searchParams.get('code') || '').trim()
  if (!code) return NextResponse.json({ valid: false })

  const { data, error } = await supabase
    .schema('waitlist')
    .from('vouchers')
    .select('campaign, status, assigned_email, expires_at')
    .eq('code', code)
    .single()

  if (error || !data) return NextResponse.json({ valid: false })
  if (data.status !== 'unused') return NextResponse.json({ valid: false })
  if (data.expires_at && new Date(data.expires_at) < new Date()) return NextResponse.json({ valid: false })

  return NextResponse.json({ valid: true, campaign: data.campaign, assignedEmail: data.assigned_email })
}


