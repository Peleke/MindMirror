import { NextRequest, NextResponse } from 'next/server'
import { createServiceRoleClient } from '../../../../../lib/supabase/server'
import { Webhook } from 'svix'

// Minimal Resend webhook to capture delivered/opened/clicked/etc.
// Configure RESEND_WEBHOOK_SECRET and set the same in Resend dashboard

export async function POST(request: NextRequest) {
  const secret = process.env.RESEND_WEBHOOK_SECRET || ''
  if (!secret) return NextResponse.json({ error: 'Webhook not configured' }, { status: 500 })

  // Resend uses Svix signatures
  const svixId = request.headers.get('svix-id') || ''
  const svixTimestamp = request.headers.get('svix-timestamp') || ''
  const svixSignature = request.headers.get('svix-signature') || ''

  const payloadText = await request.text()
  let payload: any = null
  try {
    const wh = new Webhook(secret)
    wh.verify(payloadText, {
      'svix-id': svixId,
      'svix-timestamp': svixTimestamp,
      'svix-signature': svixSignature,
    })
    payload = JSON.parse(payloadText)
  } catch (e) {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 401 })
  }
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


