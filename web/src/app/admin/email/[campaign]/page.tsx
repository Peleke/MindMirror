import { createServiceRoleClient } from '../../../../../lib/supabase/server'

interface PageProps { params: { campaign: string }, searchParams?: { [key: string]: string | string[] | undefined } }

async function getSubscribers(campaign: string) {
  const supabase = createServiceRoleClient()
  let query = supabase
    .schema('waitlist')
    .from('subscriber_campaigns')
    .select('id, subscriber_id, campaign, status, drip_day_sent, subscribed_at, subscriber:subscribers(id,email)')
    .eq('campaign', campaign)
  const { data, error } = await query
  if (error) return { subscribers: [] }
  const subscribers = (data as any[] || []).map((row: any) => ({
    subscriberCampaignId: row.id,
    subscriberId: row.subscriber_id,
    email: row.subscriber?.email,
    campaign: row.campaign,
    status: row.status,
    dripDaySent: row.drip_day_sent,
    subscribedAt: row.subscribed_at,
  }))
  return { subscribers }
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


