'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { useMemo } from 'react'

export default function CampaignSwitcher() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const selected = (searchParams.get('campaign') || '').toLowerCase()

  const options = useMemo(() => ([
    { value: '', label: 'All campaigns' },
    { value: 'mindmirror', label: 'MindMirror' },
    { value: 'uye', label: 'Unf*ck Your Eating' },
  ]), [])

  function onChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const value = e.target.value
    const params = new URLSearchParams(searchParams.toString())
    if (value) params.set('campaign', value)
    else params.delete('campaign')
    router.push(`/admin/analytics${params.toString() ? `?${params.toString()}` : ''}`)
  }

  return (
    <div className="flex items-center gap-2 mb-4">
      <label className="text-sm text-gray-600">Campaign:</label>
      <select value={selected} onChange={onChange} className="border border-gray-300 rounded-md text-sm px-2 py-1">
        {options.map(o => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  )
}


