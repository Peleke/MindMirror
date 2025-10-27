import { NextResponse } from 'next/server'
import { createServiceRoleClient } from '../../../../../../../lib/supabase/server'

export async function GET(req: Request, ctx: { params: { campaign: string } }) {
  const supabase = createServiceRoleClient()
  const campaign = (ctx.params.campaign || '').toLowerCase()

  const url = new URL(req.url)
  const status = url.searchParams.get('status') || undefined
  const day = url.searchParams.get('day') ? Number(url.searchParams.get('day')) : undefined

  let query = supabase
    .schema('waitlist')
    .from('subscriber_campaigns')
    .select('id, subscriber_id, campaign, status, drip_day_sent, subscribed_at, subscriber:subscribers(id,email)')
    .eq('campaign', campaign)

  if (status) query = query.eq('status', status)
  if (day !== undefined && !Number.isNaN(day)) query = query.eq('drip_day_sent', day)

  const { data, error } = await query
  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }

  const subscribers = (data as any[] || []).map((row: any) => ({
    subscriberCampaignId: row.id,
    subscriberId: row.subscriber_id,
    email: row.subscriber?.email,
    campaign: row.campaign,
    status: row.status,
    dripDaySent: row.drip_day_sent,
    subscribedAt: row.subscribed_at,
  }))

  return NextResponse.json({ subscribers })
}


