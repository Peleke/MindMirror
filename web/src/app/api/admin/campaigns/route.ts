import { NextResponse } from 'next/server'
import { createServiceRoleClient } from '../../../../../lib/supabase/server'

export async function GET() {
  const supabase = createServiceRoleClient()

  // Aggregate counts by campaign/status/day
  const { data, error } = await supabase
    .schema('waitlist')
    .from('subscriber_campaigns')
    .select('campaign, status, drip_day_sent, subscribed_at')

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }

  const today = new Date()
  const byCampaign: Record<string, any> = {}

  for (const row of data || []) {
    const campaign = (row.campaign || 'mindmirror').toLowerCase()
    if (!byCampaign[campaign]) {
      byCampaign[campaign] = {
        campaign,
        totals: { total: 0, active: 0, paused: 0 },
        byDay: Array.from({ length: 15 }, (_, i) => ({ day: i, count: 0 })),
        dueToday: 0,
      }
    }
    const bucket = byCampaign[campaign]
    bucket.totals.total += 1
    if (row.status === 'active') bucket.totals.active += 1
    else bucket.totals.paused += 1

    const day = Math.max(0, Math.min(14, Number(row.drip_day_sent ?? -1)))
    if (!Number.isNaN(day)) {
      bucket.byDay[day].count += 1
    }

    // dueToday = daysSince > drip_day_sent && daysSince <= 14
    const subAt = new Date(row.subscribed_at)
    const daysSince = Math.floor((Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()) - Date.UTC(subAt.getUTCFullYear(), subAt.getUTCMonth(), subAt.getUTCDate())) / (24 * 60 * 60 * 1000))
    const last = Number(row.drip_day_sent ?? -1)
    if (row.status === 'active' && daysSince > last && daysSince <= 14) {
      bucket.dueToday += 1
    }
  }

  return NextResponse.json({ campaigns: Object.values(byCampaign) })
}


