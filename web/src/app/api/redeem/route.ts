import { NextRequest, NextResponse } from 'next/server'

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

    const body = await req.json()
    const code = body.code
    if (!code) return NextResponse.json({ ok: false, reason: 'code-required' }, { status: 400 })

    // MVP: Accept a posted entitlement payload; later: look up code in DB
    const entitlement = body.entitlement
    if (!entitlement || entitlement.code !== code || entitlement.status !== 'issued' || !entitlement.programTemplateId) {
      return NextResponse.json({ ok: false, reason: 'invalid-code' }, { status: 400 })
    }

    const headers = { 'x-internal-id': internalId }
    const today = new Date().toISOString().slice(0, 10)
    await assignProgramToUser(entitlement.programTemplateId, today, headers)

    return NextResponse.json({ ok: true, programTemplateId: entitlement.programTemplateId })
  } catch (e) {
    return NextResponse.json({ ok: false }, { status: 500 })
  }
}


