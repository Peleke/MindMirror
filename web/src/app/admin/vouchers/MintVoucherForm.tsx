'use client'

import { useState } from 'react'

export default function MintVoucherForm() {
  const [email, setEmail] = useState('')
  const [campaign, setCampaign] = useState('uye')
  const [status, setStatus] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [redeemCode, setRedeemCode] = useState('')
  const [redeemEmail, setRedeemEmail] = useState('')
  const [redeemStatus, setRedeemStatus] = useState<string | null>(null)
  const origin = typeof window !== 'undefined' ? window.location.origin : ''

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setStatus(null)
    try {
      const res = await fetch('/api/vouchers/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, campaign })
      })
      if (!res.ok) {
        const j = await res.json().catch(() => ({}))
        throw new Error(j?.error || 'Failed to mint voucher')
      }
      setStatus('Voucher created and email sent')
      setEmail('')
    } catch (err: any) {
      setStatus(err?.message || 'Error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={onSubmit} className="border border-gray-200 rounded-lg p-4">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-end">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="user@example.com" className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Campaign</label>
            <select value={campaign} onChange={e => setCampaign(e.target.value)} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm">
              <option value="uye">UYE</option>
              <option value="mindmirror">MindMirror</option>
            </select>
          </div>
          <div>
            <button type="submit" disabled={loading} className="inline-flex items-center px-4 py-2 rounded-md bg-indigo-600 text-white text-sm disabled:opacity-60">
              {loading ? 'Minting…' : 'Mint & Send'}
            </button>
          </div>
        </div>
        {status && <div className="text-sm mt-2 text-gray-600">{status}</div>}
      </form>

      <div className="border border-gray-200 rounded-lg p-4">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-end">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Redeem Code</label>
            <input value={redeemCode} onChange={e => setRedeemCode(e.target.value)} placeholder="e.g. S4FGMXLJ" className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Redeem For Email (optional)</label>
            <input value={redeemEmail} onChange={e => setRedeemEmail(e.target.value)} placeholder="leave blank = current admin" className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" />
          </div>
          <div>
            <button onClick={async () => {
              setRedeemStatus(null)
              try {
                const endpoint = redeemEmail ? '/api/admin/vouchers/redeem' : '/api/vouchers/redeem'
                const payload: any = { code: redeemCode.trim() }
                if (redeemEmail) payload.email = redeemEmail
                const res = await fetch(endpoint, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify(payload)
                })
                const j = await res.json().catch(() => ({}))
                if (!res.ok) throw new Error(j?.error || 'Failed to redeem')
                setRedeemStatus('Redeemed successfully')
              } catch (e: any) {
                setRedeemStatus(e?.message || 'Error')
              }
            }} className="inline-flex items-center px-4 py-2 rounded-md bg-green-600 text-white text-sm w-full" type="button">Redeem</button>
          </div>
        </div>
        {redeemStatus && <div className="text-sm mt-2 text-gray-600">{redeemStatus}</div>}
      </div>

      <div className="border border-gray-200 rounded-lg p-4">
        <div className="text-sm text-gray-700 mb-2">cURL helper (API test):</div>
        <pre className="whitespace-pre-wrap text-xs bg-gray-50 border border-gray-200 rounded-md p-3">{`curl -X POST '${origin}/api/vouchers/redeem' \
  -H 'Content-Type: application/json' \
  -d '{"code":"${redeemCode || 'YOURCODE'}"}'`}{redeemEmail ? `

# Admin redeem for arbitrary email
curl -X POST '${origin}/api/admin/vouchers/redeem' \
  -H 'Content-Type: application/json' \
  -d '{"code":"${redeemCode || 'YOURCODE'}","email":"${redeemEmail}"}'` : ''}</pre>
      </div>
    </div>
  )
}


