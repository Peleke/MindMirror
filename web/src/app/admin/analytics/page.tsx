import { headers } from 'next/headers'
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

async function getSummary(range: string, campaign?: string) {
  const base = getBaseUrl()
  const res = await fetch(`${base}/api/admin/analytics/summary?range=${encodeURIComponent(range)}${campaign ? `&campaign=${encodeURIComponent(campaign)}` : ''}`, { cache: 'no-store' })
  if (!res.ok) return { range, summary: {} }
  return res.json()
}

async function getSeries(metric: string, range: string, campaign?: string) {
  const base = getBaseUrl()
  const res = await fetch(`${base}/api/admin/analytics/timeseries?metric=${encodeURIComponent(metric)}&range=${encodeURIComponent(range)}&bucket=day${campaign ? `&campaign=${encodeURIComponent(campaign)}` : ''}`, { cache: 'no-store' })
  if (!res.ok) return { series: [] }
  return res.json()
}

export default async function AnalyticsPage({ searchParams }: { searchParams?: { [k: string]: string | string[] | undefined } }) {
  const range = '7d'
  const campaign = (searchParams?.campaign as string | undefined) || ''
  const [summary, series] = await Promise.all([
    getSummary(range, campaign || undefined),
    getSeries('opened', range, campaign || undefined)
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
        <div className="text-sm text-gray-700 mb-3">Opens over time (last 7 days)</div>
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


