import { createClient } from '../../../../../lib/supabase/server'
import { redirect } from 'next/navigation'
import { isUserAdmin } from '../../../../../lib/supabase/admin'
import MagicLinkForm from './MagicLinkForm'

export default async function MagicLinkPage() {
  const supabase = await createClient()

  const { data: { user }, error } = await supabase.auth.getUser()

  if (error || !user) {
    redirect('/admin/login')
  }

  // Check if user is admin
  const isAdmin = await isUserAdmin(user.id)

  if (!isAdmin) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-red-800 mb-2">Access Denied</h2>
          <p className="text-red-700">Admin privileges required to access this page.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-semibold">Magic Link Generator</h1>
          <p className="text-sm text-gray-600 mt-1">Create magic links for alpha user onboarding</p>
        </div>
        <a href="/admin" className="text-sm text-gray-600 hover:text-gray-800">Back to Dashboard</a>
      </div>
      <MagicLinkForm />
    </div>
  )
}
