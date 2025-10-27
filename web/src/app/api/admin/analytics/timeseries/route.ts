import { NextResponse } from 'next/server'
import { createServiceRoleClient } from '../../../../../../lib/supabase/server'

function parseRange(range?: string) {
  const now = new Date()
  const days = range === '30d' ? 30 : 7
  const from = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
  return { from, to: now, days }
}

export async function GET(request: Request) {
  const supabase = createServiceRoleClient()
  const { searchParams } = new URL(request.url)
  const metric = (searchParams.get('metric') || 'opened').toLowerCase()
  const bucket = (searchParams.get('bucket') || 'day').toLowerCase()
  const range = searchParams.get('range') || '7d'
  const campaignFilter = (searchParams.get('campaign') || '').toLowerCase() || undefined

  const { from, to, days } = parseRange(range)

  const { data, error } = await supabase
    .schema('waitlist')
    .from('email_events')
    .select('created_at, event_type, event_data')
    .eq('event_type', metric)
    .gte('created_at', from.toISOString())
    .lte('created_at', to.toISOString())

  if (error) return NextResponse.json({ error: error.message }, { status: 500 })

  // Initialize buckets
  const buckets: { date: string, count: number }[] = []
  const cursor = new Date(from)
  for (let i = 0; i < days; i++) {
    const key = cursor.toISOString().slice(0, 10)
    buckets.push({ date: key, count: 0 })
    cursor.setUTCDate(cursor.getUTCDate() + 1)
  }

  // Tally counts
  for (const row of data || []) {
    if (campaignFilter) {
      const rowCampaign = (row.event_data?.campaign || row.event_data?.tags?.find?.((t: any) => t.name === 'campaign')?.value || '').toLowerCase()
      if (rowCampaign !== campaignFilter) continue
    }
    const key = new Date(row.created_at).toISOString().slice(0, 10)
    const idx = buckets.findIndex(b => b.date === key)
    if (idx >= 0) buckets[idx].count += 1
  }

  return NextResponse.json({ metric, range, bucket, series: buckets })
}


