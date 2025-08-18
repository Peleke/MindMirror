import { NextRequest, NextResponse } from 'next/server'
import { createServiceRoleClient } from '../../../../../lib/supabase/server'

// Minimal Resend webhook to capture delivered/opened/clicked/etc.
// Configure RESEND_WEBHOOK_SECRET and set the same in Resend dashboard

export async function POST(request: NextRequest) {
  const secret = process.env.RESEND_WEBHOOK_SECRET || ''
  const header = request.headers.get('x-resend-signature') || ''
  if (!secret) return NextResponse.json({ error: 'Webhook not configured' }, { status: 500 })

  // For simplicity, accept when header equals secret. Replace with HMAC verification if desired.
  if (header !== secret) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const payload = await request.json().catch(() => null as any)
  if (!payload) return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 })

  const supabase = createServiceRoleClient()

  const events: any[] = Array.isArray(payload) ? payload : [payload]
  const inserts: any[] = []

  for (const evt of events) {
    const type = (evt.type || evt.event || '').toLowerCase() || 'unknown'
    const messageId = evt?.data?.id || evt?.data?.email_id || evt?.id
    const tags = evt?.data?.tags || evt?.tags || []
    const campaign = evt?.data?.campaign || (tags.find?.((t: any) => t.name === 'campaign')?.value)
    const day = Number(evt?.data?.day || (tags.find?.((t: any) => t.name === 'day')?.value))
    const subscriberId = evt?.data?.subscriber_id || (tags.find?.((t: any) => t.name === 'subscriber_id')?.value)

    inserts.push({
      subscriber_id: subscriberId ? Number(subscriberId) : null,
      email_id: messageId,
      event_type: type,
      event_data: evt,
    })
  }

  if (inserts.length > 0) {
    const { error } = await supabase
      .schema('waitlist')
      .from('email_events')
      .insert(inserts)
    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }
  }

  return NextResponse.json({ ok: true })
}


