import { createServiceRoleClient } from './server'
import { Database } from './types'

type AdminUser = Database['waitlist']['Tables']['admin_users']['Row']

// Create an admin user (call this during setup)
export async function createAdminUser(email: string, password: string): Promise<{ user: any; adminRecord: AdminUser | null; error: any }> {
  const supabase = createServiceRoleClient()
  
  try {
    console.log('Creating admin user with service role client...')
    
    // Create user in auth.users
    const { data: authData, error: authError } = await supabase.auth.admin.createUser({
      email,
      password,
      email_confirm: true // Skip email confirmation for admin
    })

    console.log('Auth user creation result:', {
      success: !!authData.user,
      userId: authData.user?.id,
      email: authData.user?.email,
      error: authError
    })

    if (authError || !authData.user) {
      return { user: null, adminRecord: null, error: authError }
    }

    console.log('Attempting to create admin record in admin_users...')

    // Create admin record
    const { data: adminData, error: adminError } = await supabase
      .from('admin_users')
      .insert({
        user_id: authData.user.id,
        role: 'admin'
      })
      .select()
      .single()

    console.log('Admin record creation result:', {
      success: !!adminData,
      adminId: adminData?.id,
      error: adminError,
      errorMessage: adminError?.message,
      errorCode: adminError?.code,
      errorDetails: adminError?.details,
      errorHint: adminError?.hint
    })

    if (adminError) {
      console.log('Admin record creation failed, cleaning up auth user...')
      // Cleanup: delete the user if admin record creation failed
      await supabase.auth.admin.deleteUser(authData.user.id)
      
      // Return a properly serializable error
      return { 
        user: null, 
        adminRecord: null, 
        error: {
          message: adminError.message || 'Unknown database error',
          code: adminError.code || 'DB_ERROR',
          details: adminError.details || 'Failed to create admin record',
          hint: adminError.hint || 'Check if admin_users table exists'
        }
      }
    }

    return { user: authData.user, adminRecord: adminData, error: null }
  } catch (error) {
    console.error('Exception in createAdminUser:', error)
    return { 
      user: null, 
      adminRecord: null, 
      error: {
        message: error instanceof Error ? error.message : 'Unknown error',
        type: 'EXCEPTION',
        details: error
      }
    }
  }
}

// Check if a user is an admin
export async function isUserAdmin(userId: string): Promise<boolean> {
  const supabase = createServiceRoleClient()
  
  try {
    const { data, error } = await supabase
      .from('admin_users')
      .select('id')
      .eq('user_id', userId)
      .single()

    return !error && !!data
  } catch (error) {
    return false
  }
}

// Get admin profile
export async function getAdminProfile(userId: string): Promise<AdminUser | null> {
  const supabase = createServiceRoleClient()
  
  try {
    const { data, error } = await supabase
      .from('admin_users')
      .select('*')
      .eq('user_id', userId)
      .single()

    return error ? null : data
  } catch (error) {
    return null
  }
}

// List all admin users (for super admin functionality)
export async function getAllAdmins(): Promise<AdminUser[]> {
  const supabase = createServiceRoleClient()
  
  try {
    const { data, error } = await supabase
      .from('admin_users')
      .select('*')
      .order('created_at', { ascending: false })

    return error ? [] : (data || [])
  } catch (error) {
    return []
  }
} 