'use client'

import { useState } from 'react'

export default function ForceDripPage() {
  const [email, setEmail] = useState('')
  const [campaign, setCampaign] = useState<'mindmirror'|'uye'>('uye')
  const [day, setDay] = useState(0)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  async function onSend() {
    setLoading(true)
    setResult(null)
    try {
      if (!email) {
        setResult({ error: 'email required' })
        return
      }
      const res = await fetch('/api/admin/drip/force-send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, day, campaign })
      })
      const j = await res.json().catch(() => ({}))
      setResult(j)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold">Force Drip Email</h1>
        <a href="/admin" className="text-sm text-gray-600 hover:text-gray-800">Back to Dashboard</a>
      </div>
      <div className="border border-gray-200 rounded-lg p-4 space-y-3">
        <div>
          <label className="block text-sm text-gray-600 mb-1">Email</label>
          <input className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" value={email} onChange={e => setEmail(e.target.value)} placeholder="user@example.com" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Campaign</label>
            <select className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" value={campaign} onChange={e => setCampaign(e.target.value as any)}>
              <option value="uye">UYE</option>
              <option value="mindmirror">MindMirror</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Day</label>
            <input type="number" min={0} max={14} className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" value={day} onChange={e => setDay(parseInt(e.target.value || '0', 10))} />
          </div>
        </div>
        <button onClick={onSend} disabled={loading} className="inline-flex items-center px-4 py-2 rounded-md bg-indigo-600 text-white text-sm disabled:opacity-60">{loading ? 'Sending…' : 'Send'}</button>
        {result && (
          <pre className="text-xs bg-gray-50 border border-gray-200 rounded p-3 whitespace-pre-wrap">{JSON.stringify(result, null, 2)}</pre>
        )}
      </div>
    </div>
  )
}


