import { NextResponse } from 'next/server'
import { createServiceRoleClient } from '../../../../../lib/supabase/server'

export async function GET() {
  const supabase = createServiceRoleClient()
  const { data, error } = await supabase
    .schema('waitlist')
    .from('subscribers')
    .select('id,email,subscribed_at,source,status')
    .order('subscribed_at', { ascending: false })
    .limit(200)

  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return NextResponse.json({ subscribers: data || [] })
}