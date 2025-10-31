import { NextResponse } from 'next/server'
import { createServiceRoleClient } from '../../../../../../lib/supabase/server'

function parseRange(range?: string) {
  const now = new Date()
  const days = range === '30d' ? 30 : 7
  const from = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
  return { from, to: now }
}

export async function GET(request: Request) {
  const supabase = createServiceRoleClient()
  const { searchParams } = new URL(request.url)
  const range = searchParams.get('range') || '7d'
  const campaignFilter = (searchParams.get('campaign') || '').toLowerCase() || undefined
  const { from, to } = parseRange(range)

  const { data, error } = await supabase
    .schema('waitlist')
    .from('email_events')
    .select('event_type, created_at, event_data')
    .gte('created_at', from.toISOString())
    .lte('created_at', to.toISOString())

  if (error) return NextResponse.json({ error: error.message }, { status: 500 })

  const summary: Record<string, number> = {}
  for (const row of data || []) {
    if (campaignFilter) {
      const rowCampaign = (row.event_data?.campaign || row.event_data?.tags?.find?.((t: any) => t.name === 'campaign')?.value || '').toLowerCase()
      if (rowCampaign !== campaignFilter) continue
    }
    const type = (row.event_type || 'sent').toLowerCase()
    summary[type] = (summary[type] || 0) + 1
  }

  return NextResponse.json({ range, summary })
}


