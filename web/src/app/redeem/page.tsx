'use client'

import { useEffect, useMemo, useState } from 'react'

export default function RedeemPage() {
  const params = useMemo(() => new URLSearchParams(typeof window !== 'undefined' ? window.location.search : ''), [])
  const [code, setCode] = useState(params.get('code') || '')
  const [status, setStatus] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const initial = params.get('code')
    if (initial) {
      redeem(initial)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function redeem(c: string) {
    setLoading(true)
    setStatus(null)
    try {
      const res = await fetch('/api/vouchers/redeem', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: c.trim() })
      })
      const j = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(j?.error || 'Failed to redeem')
      setStatus('Redeemed successfully. You now have access.')
    } catch (e: any) {
      if (e?.message === 'unauthorized') setStatus('Please sign in to redeem your voucher.')
      else setStatus(e?.message || 'Error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-4">Redeem Voucher</h1>
      <p className="text-sm text-gray-600 mb-4">If you followed a link from your email, redemption will start automatically. Otherwise, enter your code below.</p>
      <div className="space-y-3">
        <input value={code} onChange={e => setCode(e.target.value)} placeholder="Enter your voucher code" className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" />
        <button disabled={loading || !code} onClick={() => redeem(code)} className="w-full inline-flex items-center justify-center px-4 py-2 rounded-md bg-indigo-600 text-white text-sm disabled:opacity-60">
          {loading ? 'Redeeming…' : 'Redeem'}
        </button>
        {status && <div className="text-sm text-gray-700">{status}</div>}
      </div>
    </div>
  )
}


