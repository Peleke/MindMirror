import { headers } from 'next/headers'
import { createServiceRoleClient } from '../../../../lib/supabase/server'
import CampaignSwitcher from './CampaignSwitcher'

function getBaseUrl() {
  try {
    const h = headers()
    const host = (h as any).get('x-forwarded-host') || (h as any).get('host')
    const proto = (h as any).get('x-forwarded-proto') || 'https'
    if (host) return `${proto}://${host}`
  } catch {}
  if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}`
  if (process.env.NEXT_PUBLIC_BASE_URL) return process.env.NEXT_PUBLIC_BASE_URL.replace(/\/$/, '')
  return 'http://localhost:3000'
}

function parseRange(range?: string) {
  const now = new Date()
  const days = range === '30d' ? 30 : 7
  const from = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
  return { from, to: now, days }
}

async function getSummaryDirect(range: string, campaign?: string) {
  const supabase = createServiceRoleClient()
  const { from, to } = parseRange(range)
  const { data, error } = await supabase
    .schema('waitlist')
    .from('email_events')
    .select('event_type, created_at, event_data')
    .gte('created_at', from.toISOString())
    .lte('created_at', to.toISOString())
  if (error) return { range, summary: {} as Record<string, number> }
  const summary: Record<string, number> = {}
  for (const row of data || []) {
    if (campaign) {
      const rowCampaign = (row as any).event_data?.campaign || (row as any).event_data?.tags?.find?.((t: any) => t.name === 'campaign')?.value
      if ((rowCampaign || '').toLowerCase() !== campaign.toLowerCase()) continue
    }
    const type = ((row as any).event_type || 'sent').toLowerCase()
    summary[type] = (summary[type] || 0) + 1
  }
  return { range, summary }
}

async function getSeriesDirect(metric: string, range: string, campaign?: string) {
  const supabase = createServiceRoleClient()
  const { from, to, days } = parseRange(range)
  const { data, error } = await supabase
    .schema('waitlist')
    .from('email_events')
    .select('created_at, event_type, event_data')
    .eq('event_type', metric)
    .gte('created_at', from.toISOString())
    .lte('created_at', to.toISOString())
  if (error) return { series: [] as Array<{ date: string, count: number }> }
  const buckets: { date: string, count: number }[] = []
  const cursor = new Date(from)
  for (let i = 0; i < days; i++) {
    const key = cursor.toISOString().slice(0, 10)
    buckets.push({ date: key, count: 0 })
    cursor.setUTCDate(cursor.getUTCDate() + 1)
  }
  for (const row of data || []) {
    if (campaign) {
      const rowCampaign = (row as any).event_data?.campaign || (row as any).event_data?.tags?.find?.((t: any) => t.name === 'campaign')?.value
      if ((rowCampaign || '').toLowerCase() !== campaign.toLowerCase()) continue
    }
    const key = new Date((row as any).created_at).toISOString().slice(0, 10)
    const idx = buckets.findIndex(b => b.date === key)
    if (idx >= 0) buckets[idx].count += 1
  }
  return { series: buckets }
}

export default async function AnalyticsPage({ searchParams }: { searchParams?: { [k: string]: string | string[] | undefined } }) {
  const range = '7d'
  const campaign = (searchParams?.campaign as string | undefined) || ''
  const [summary, series] = await Promise.all([
    getSummaryDirect(range, campaign || undefined),
    getSeriesDirect('sent', range, campaign || undefined)
  ])

  const s = summary.summary || {}
  const seriesData = series.series || []

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-2">Email Analytics</h1>
      <CampaignSwitcher />
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="border border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-500">Sent</div>
          <div className="text-2xl font-semibold">{s.sent || 0}</div>
        </div>
        <div className="border border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-500">Delivered</div>
          <div className="text-2xl font-semibold">{s.delivered || 0}</div>
        </div>
        <div className="border border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-500">Opened</div>
          <div className="text-2xl font-semibold">{s.opened || 0}</div>
        </div>
        <div className="border border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-500">Clicked</div>
          <div className="text-2xl font-semibold">{s.clicked || 0}</div>
        </div>
      </div>

      <div className="border border-gray-200 rounded-lg p-4">
        <div className="text-sm text-gray-700 mb-3">Sends over time (last 7 days)</div>
        <div className="w-full overflow-x-auto">
          <div className="flex items-end h-40 gap-2">
            {seriesData.map((d: any) => (
              <div key={d.date} className="flex flex-col items-center">
                <div className="bg-indigo-500 w-6" style={{ height: `${Math.min(100, d.count * 10)}px` }} />
                <div className="text-[10px] text-gray-500 mt-1">{d.date.slice(5)}</div>
              </div>
            ))}
            {seriesData.length === 0 && (
              <div className="text-sm text-gray-500">No data</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}


