import { headers } from 'next/headers'

interface PageProps { params: { campaign: string }, searchParams?: { [key: string]: string | string[] | undefined } }

function getBaseUrl() {
  try {
    const h = headers()
    const host = (h as any).get('x-forwarded-host') || (h as any).get('host')
    const proto = (h as any).get('x-forwarded-proto') || 'http'
    if (host) return `${proto}://${host}`
  } catch {}
  if (process.env.NEXT_PUBLIC_BASE_URL) return process.env.NEXT_PUBLIC_BASE_URL.replace(/\/$/, '')
  if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}`
  return 'http://localhost:3000'
}

async function getSubscribers(campaign: string) {
  const base = getBaseUrl()
  const res = await fetch(`${base}/api/admin/campaigns/${campaign}/subscribers`, { cache: 'no-store' })
  if (!res.ok) return { subscribers: [] }
  return res.json()
}

export default async function CampaignDetailPage({ params }: PageProps) {
  const { campaign } = params
  const { subscribers } = await getSubscribers(campaign)
  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-4 capitalize">{campaign} — Subscribers</h1>
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Day</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subscribed</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {subscribers.map((s: any) => (
              <tr key={s.subscriberCampaignId}>
                <td className="px-4 py-2 text-sm text-gray-900">{s.email}</td>
                <td className="px-4 py-2 text-sm">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${s.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>{s.status}</span>
                </td>
                <td className="px-4 py-2 text-sm text-gray-700">{s.dripDaySent}</td>
                <td className="px-4 py-2 text-sm text-gray-500">{new Date(s.subscribedAt).toLocaleDateString()}</td>
              </tr>
            ))}
            {subscribers.length === 0 && (
              <tr><td className="px-4 py-6 text-center text-gray-500" colSpan={4}>No subscribers</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}


