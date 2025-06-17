import { NextRequest, NextResponse } from 'next/server'
import { createAdminUser } from '../../../../../lib/supabase/admin'

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()

    if (!email || !password) {
      return NextResponse.json({ error: 'Email and password required' }, { status: 400 })
    }

    // Basic validation
    if (password.length < 8) {
      return NextResponse.json({ error: 'Password must be at least 8 characters' }, { status: 400 })
    }

    console.log('Attempting to create admin user:', email)
    
    const result = await createAdminUser(email, password)
    
    console.log('createAdminUser result:', {
      user: result.user ? 'User created' : 'No user',
      adminRecord: result.adminRecord ? 'Admin record created' : 'No admin record',
      error: result.error
    })

    if (result.error) {
      console.error('Admin creation error details:', {
        error: result.error,
        message: result.error?.message,
        code: result.error?.code,
        details: result.error?.details
      })
      return NextResponse.json({ 
        error: result.error.message || result.error.toString() || 'Failed to create admin',
        details: result.error
      }, { status: 400 })
    }

    return NextResponse.json({ 
      success: true, 
      message: 'Admin user created successfully',
      adminId: result.adminRecord?.id 
    })
  } catch (error) {
    console.error('Admin setup error:', error)
    return NextResponse.json({ 
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
} 