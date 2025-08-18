import Link from 'next/link'
import { headers } from 'next/headers'

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

async function getCampaigns() {
  const base = getBaseUrl()
  const res = await fetch(`${base}/api/admin/campaigns`, { cache: 'no-store' })
  if (!res.ok) return { campaigns: [] }
  return res.json()
}

export default async function CampaignListPage() {
  const { campaigns } = await getCampaigns()

  return (
    <div className="max-w-5xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-4">Email Campaigns</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {campaigns.map((c: any) => (
          <Link key={c.campaign} href={`/admin/email/${c.campaign}`} className="block border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-lg font-medium capitalize">{c.campaign}</div>
                <div className="text-sm text-gray-500">Active: {c.totals.active} • Paused: {c.totals.paused} • Total: {c.totals.total}</div>
                <div className="text-xs text-gray-400 mt-1">Due today: {c.dueToday}</div>
              </div>
            </div>
          </Link>
        ))}
      </div>
      {(!campaigns || campaigns.length === 0) && (
        <div className="text-gray-500">No campaigns found</div>
      )}
    </div>
  )
}


