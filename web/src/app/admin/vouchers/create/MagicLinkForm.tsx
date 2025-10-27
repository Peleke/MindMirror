'use client'

import { useState, useEffect } from 'react'
import { Copy, CheckCircle, AlertCircle } from 'lucide-react'

interface Program {
  id_: string
  name: string
  description?: string
}

interface MagicLinkResponse {
  magicLink: string
  voucherId: string
  code: string
  emailSent?: boolean
  programName?: string
}

export default function MagicLinkForm() {
  const [email, setEmail] = useState('')
  const [programId, setProgramId] = useState('')
  const [expirationDate, setExpirationDate] = useState('')
  const [personalMessage, setPersonalMessage] = useState('')
  const [sendEmail, setSendEmail] = useState(true)
  const [loading, setLoading] = useState(false)
  const [loadingPrograms, setLoadingPrograms] = useState(true)
  const [programs, setPrograms] = useState<Program[]>([])
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<MagicLinkResponse | null>(null)
  const [copied, setCopied] = useState(false)

  // Fetch programs on mount
  useEffect(() => {
    const fetchPrograms = async () => {
      try {
        // GraphQL query to fetch all programs
        const query = `
          query GetPrograms {
            programs {
              id_
              name
              description
            }
          }
        `

        const response = await fetch('/api/graphql', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query })
        })

        const result = await response.json()

        if (result.errors) {
          console.error('Failed to fetch programs:', result.errors)
          setError('Failed to load programs. Please refresh the page.')
        } else if (result.data?.programs) {
          setPrograms(result.data.programs)
        }
      } catch (err) {
        console.error('Error fetching programs:', err)
        setError('Failed to load programs. Please refresh the page.')
      } finally {
        setLoadingPrograms(false)
      }
    }

    fetchPrograms()
  }, [])

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const validateProgramId = (id: string): boolean => {
    // UUID v4 validation
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
    return uuidRegex.test(id)
  }

  const handleCopy = async () => {
    if (!result) return

    try {
      await navigator.clipboard.writeText(result.magicLink)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      // Validate email format
      if (!validateEmail(email)) {
        throw new Error('Invalid email format')
      }

      // Validate program ID format
      if (!validateProgramId(programId)) {
        throw new Error('Invalid program ID format (must be a valid UUID)')
      }

      // Call the API to create voucher and magic link
      const res = await fetch('/api/vouchers/create-magic-link', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.toLowerCase().trim(),
          programId: programId.trim(),
          expirationDate: expirationDate || null,
          personalMessage: personalMessage.trim() || null,
          sendEmail
        })
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.error || 'Failed to create magic link')
      }

      setResult(data)

      // Clear form on success
      setEmail('')
      setProgramId('')
      setExpirationDate('')
      setPersonalMessage('')
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Form */}
      <form onSubmit={handleSubmit} className="border border-gray-200 rounded-lg p-6 space-y-4">
        {/* Email Input */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            Email Address *
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="user@example.com"
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500 mt-1">Alpha user's email address</p>
        </div>

        {/* Program Select */}
        <div>
          <label htmlFor="programId" className="block text-sm font-medium text-gray-700 mb-1">
            Workout Program *
          </label>
          {loadingPrograms ? (
            <div className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm text-gray-500">
              Loading programs...
            </div>
          ) : (
            <select
              id="programId"
              value={programId}
              onChange={(e) => setProgramId(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="">Select a program...</option>
              {programs.map((program) => (
                <option key={program.id_} value={program.id_}>
                  {program.name}
                </option>
              ))}
            </select>
          )}
          <p className="text-xs text-gray-500 mt-1">Workout program to assign to the user</p>
        </div>

        {/* Personal Message */}
        <div>
          <label htmlFor="personalMessage" className="block text-sm font-medium text-gray-700 mb-1">
            Personal Message (optional)
          </label>
          <textarea
            id="personalMessage"
            value={personalMessage}
            onChange={(e) => setPersonalMessage(e.target.value)}
            rows={3}
            placeholder="Add a personal message to include in the email..."
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500 mt-1">This message will be included in the email to the user</p>
        </div>

        {/* Send Email Checkbox */}
        <div className="flex items-center space-x-2">
          <input
            id="sendEmail"
            type="checkbox"
            checked={sendEmail}
            onChange={(e) => setSendEmail(e.target.checked)}
            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
          />
          <label htmlFor="sendEmail" className="text-sm font-medium text-gray-700">
            Send email to user with magic link
          </label>
        </div>

        {/* Expiration Date Input */}
        <div>
          <label htmlFor="expiration" className="block text-sm font-medium text-gray-700 mb-1">
            Expiration Date (optional)
          </label>
          <input
            id="expiration"
            type="date"
            value={expirationDate}
            onChange={(e) => setExpirationDate(e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500 mt-1">Leave blank for no expiration</p>
        </div>

        {/* Submit Button */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200"
          >
            {loading ? 'Generating Magic Link...' : 'Generate Magic Link'}
          </button>
        </div>
      </form>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-red-800">Error</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Success Display */}
      {result && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 space-y-4">
          <div className="flex items-start space-x-3">
            <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-green-800 mb-2">Magic Link Created Successfully!</h3>

              <div className="space-y-3">
                {/* Magic Link */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Magic Link</label>
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 bg-white border border-green-300 rounded-md px-3 py-2 text-sm font-mono break-all">
                      {result.magicLink}
                    </div>
                    <button
                      onClick={handleCopy}
                      className="flex-shrink-0 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md transition-colors duration-200 flex items-center space-x-2"
                    >
                      {copied ? (
                        <>
                          <CheckCircle className="h-4 w-4" />
                          <span className="text-sm">Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="h-4 w-4" />
                          <span className="text-sm">Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Voucher Details */}
                <div className="grid grid-cols-2 gap-4 pt-2">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Voucher Code</label>
                    <div className="bg-white border border-gray-200 rounded px-2 py-1 text-sm font-mono">
                      {result.code}
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Voucher ID</label>
                    <div className="bg-white border border-gray-200 rounded px-2 py-1 text-xs font-mono truncate">
                      {result.voucherId}
                    </div>
                  </div>
                </div>
              </div>

              <p className="text-sm text-gray-600 mt-4">
                {result.emailSent
                  ? `Email sent successfully to ${email}. The user will receive the magic link shortly.`
                  : 'Send this magic link to the alpha user to complete onboarding.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Helper Text */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">How it works</h4>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>Enter the alpha user's email and select a workout program</li>
          <li>A unique voucher is created and linked to the program</li>
          <li>The magic link includes the voucher code for automatic enrollment</li>
          <li>User clicks the link, signs up, and is automatically enrolled in the program</li>
        </ul>
      </div>
    </div>
  )
}
