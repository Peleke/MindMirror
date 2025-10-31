import { NextRequest, NextResponse } from 'next/server'

function resolveFunctionsUrl() {
  const envFn = process.env.SUPABASE_FUNCTIONS_URL || process.env.NEXT_PUBLIC_SUPABASE_FUNCTIONS_URL
  if (envFn) return envFn.replace(/\/$/, '')
  const supa = (process.env.SUPABASE_URL || '').replace(/\/$/, '')
  if (!supa) return ''
  if (supa.includes('localhost')) return `${supa}/functions/v1`
  try {
    const u = new URL(supa)
    const host = u.host.replace('.supabase.co', '.functions.supabase.co')
    return `${u.protocol}//${host}`
  } catch {
    return supa
  }
}

export async function POST(req: NextRequest) {
  const { email, day = 0, campaign = 'mindmirror' } = await req.json().catch(() => ({}))
  if (!email) return NextResponse.json({ error: 'email required' }, { status: 400 })
  const base = resolveFunctionsUrl()
  const url = `${base}/send_drip_emails`
  const cronSecret = process.env.CRON_SECRET || ''
  try {
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'x-cron-secret': cronSecret },
      body: JSON.stringify({ forceSendForEmail: email, day: Number(day), campaign: String(campaign) })
    })
    const text = await resp.text().catch(() => '')
    return NextResponse.json({ ok: resp.ok, status: resp.status, body: text })
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'failed' }, { status: 500 })
  }
}


