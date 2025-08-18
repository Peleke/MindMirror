import Link from 'next/link'
import { createServiceRoleClient } from '../../../../lib/supabase/server'

async function getCampaignsDirect() {
  const supabase = createServiceRoleClient()
  const { data, error } = await supabase
    .schema('waitlist')
    .from('subscriber_campaigns')
    .select('campaign, status, drip_day_sent, subscribed_at')
  if (error) return { campaigns: [] }
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
    if (!Number.isNaN(day)) bucket.byDay[day].count += 1
    const subAt = new Date(row.subscribed_at)
    const daysSince = Math.floor((Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()) - Date.UTC(subAt.getUTCFullYear(), subAt.getUTCMonth(), subAt.getUTCDate())) / (24 * 60 * 60 * 1000))
    const last = Number(row.drip_day_sent ?? -1)
    if (row.status === 'active' && daysSince > last && daysSince <= 14) bucket.dueToday += 1
  }
  return { campaigns: Object.values(byCampaign) }
}

export default async function CampaignListPage() {
  const { campaigns } = await getCampaignsDirect()

  return (
    <div className="max-w-5xl mx-auto p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold">Email Campaigns</h1>
        <a href="/admin" className="text-sm text-gray-600 hover:text-gray-800">Back to Dashboard</a>
      </div>
      <div className="flex items-center justify-end mb-4">
        <a href="/admin/email/force" className="text-sm text-indigo-600 hover:underline">Force-send drip email</a>
      </div>
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


