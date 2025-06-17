import { createClient } from '../../../lib/supabase/server'
import { redirect } from 'next/navigation'
import { isUserAdmin } from '../../../lib/supabase/admin'
import AdminDashboard from './AdminDashboard'

export default async function AdminPage() {
  const supabase = await createClient()
  
  const { data: { user }, error } = await supabase.auth.getUser()

  if (error || !user) {
    redirect('/admin/login')
  }

  // Check if user is admin
  const isAdmin = await isUserAdmin(user.id)
  
  if (!isAdmin) {
    redirect('/admin/login')
  }

  return <AdminDashboard user={user} />
} 