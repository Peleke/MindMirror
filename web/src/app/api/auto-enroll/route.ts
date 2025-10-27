import { NextRequest, NextResponse } from 'next/server'

// Minimal provider-agnostic auto-enroll endpoint.
// MVP: expects client to pass email and optional entitlements payload.
// Later: replace with server-side DB lookup of entitlements by email.

async function assignProgramToUser(programId: string, startDate: string, headers: Record<string, string>) {
  const gatewayUrl = process.env.NEXT_PUBLIC_GATEWAY_URL || process.env.GATEWAY_URL
  const mutation = `mutation Assign($programId: String!, $startDate: Date!) { assignProgramToUser(programId: $programId, startDate: $startDate) { id } }`
  const resp = await fetch(`${gatewayUrl}/graphql`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', ...headers },
    body: JSON.stringify({ query: mutation, variables: { programId, startDate } }),
  })
  const json = await resp.json()
  if (json.errors) throw new Error('GraphQL error')
  return json.data.assignProgramToUser
}

export async function POST(req: NextRequest) {
  try {
    const internalId = req.headers.get('x-internal-id') || ''
    if (!internalId) return NextResponse.json({ ok: false, reason: 'unauthorized' }, { status: 401 })

    const { email, entitlements } = await req.json()
    if (!email) return NextResponse.json({ ok: false, reason: 'email-required' }, { status: 400 })

    const headers = { 'x-internal-id': internalId }
    const today = new Date().toISOString().slice(0, 10)
    const assigned: string[] = []

    for (const e of entitlements ?? []) {
      if (e.status === 'issued' && e.email?.toLowerCase() === email.toLowerCase() && e.programTemplateId) {
        await assignProgramToUser(e.programTemplateId, today, headers)
        assigned.push(e.programTemplateId)
      }
    }

    return NextResponse.json({ ok: true, assigned })
  } catch (e) {
    return NextResponse.json({ ok: false }, { status: 500 })
  }
}
