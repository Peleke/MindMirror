import { NextResponse } from 'next/server'
import { createServiceRoleClient } from '../../../../../../lib/supabase/server'

export async function GET(req: Request, ctx: { params: { id: string } }) {
  const supabase = createServiceRoleClient()
  const id = Number(ctx.params.id)
  if (!id || Number.isNaN(id)) return NextResponse.json({ error: 'invalid id' }, { status: 400 })

  const { data: sub, error: subErr } = await supabase
    .schema('waitlist')
    .from('subscribers')
    .select('id,email,subscribed_at,source,status')
    .eq('id', id)
    .single()
  if (subErr) return NextResponse.json({ error: subErr.message }, { status: 500 })

  const { data: campaigns, error: campErr } = await supabase
    .schema('waitlist')
    .from('subscriber_campaigns')
    .select('campaign,status,drip_day_sent,subscribed_at')
    .eq('subscriber_id', id)
  if (campErr) return NextResponse.json({ error: campErr.message }, { status: 500 })

  const { data: events } = await supabase
    .schema('waitlist')
    .from('email_events')
    .select('created_at,event_type,event_data')
    .eq('subscriber_id', id)
    .order('created_at', { ascending: false })
    .limit(10)

  return NextResponse.json({
    subscriber: sub,
    campaigns: campaigns || [],
    recentEvents: events || [],
  })
}
