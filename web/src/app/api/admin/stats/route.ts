import { NextResponse } from 'next/server'
import { createServiceRoleClient } from '../../../../../lib/supabase/server'

// Single, consolidated stats handler (service-role, server-only)
export async function GET() {
  const supabase = createServiceRoleClient()

  const [subs, events] = await Promise.all([
    supabase
      .schema('waitlist')
      .from('subscribers')
      .select('id,status,subscribed_at'),
    supabase
      .schema('waitlist')
      .from('email_events')
      .select('id')
  ])

  if (subs.error) return NextResponse.json({ error: subs.error.message }, { status: 500 })
  if (events.error) return NextResponse.json({ error: events.error.message }, { status: 500 })

  const total = subs.data?.length || 0
  const active = subs.data?.filter(s => s.status === 'active').length || 0
  const recentCutoff = Date.now() - 7 * 24 * 60 * 60 * 1000
  const recentSignups = subs.data?.filter(s => new Date(s.subscribed_at).getTime() >= recentCutoff).length || 0
  const totalSent = events.data?.length || 0

  return NextResponse.json({
    subscribers: { total, active, recentSignups },
    emails: { totalSent, deliveryRate: 0, openRate: 0, clickRate: 0 },
  })
}