import { NextRequest, NextResponse } from 'next/server'
import { isUserAdmin } from '../../../../../lib/supabase/admin'

export async function POST(request: NextRequest) {
  try {
    const { userId } = await request.json()

    if (!userId) {
      return NextResponse.json({ error: 'User ID required' }, { status: 400 })
    }

    const isAdmin = await isUserAdmin(userId)

    if (isAdmin) {
      return NextResponse.json({ success: true })
    } else {
      return NextResponse.json({ error: 'Not an admin' }, { status: 403 })
    }
  } catch (error) {
    console.error('Admin verification error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
} 