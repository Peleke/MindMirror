import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '../../../../../lib/supabase/server'
import { isUserAdmin } from '../../../../../lib/supabase/admin'
import { getSubscriberStats, getOverallEmailStats } from '../../../../../lib/supabase/subscribers'

export async function GET(request: NextRequest) {
  try {
    const supabase = await createClient()
    
    // Check authentication
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Check if user is admin
    const isAdmin = await isUserAdmin(user.id)
    if (!isAdmin) {
      return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
    }

    // Fetch statistics
    const [subscriberStats, emailStats] = await Promise.all([
      getSubscriberStats(),
      getOverallEmailStats()
    ])

    if (subscriberStats.error) {
      console.error('Error fetching subscriber stats:', subscriberStats.error)
    }

    if (emailStats.error) {
      console.error('Error fetching email stats:', emailStats.error)
    }

    return NextResponse.json({
      subscribers: {
        total: subscriberStats.total,
        active: subscriberStats.active,
        recentSignups: subscriberStats.recentSignups
      },
      emails: {
        totalSent: emailStats.totalEmails,
        deliveryRate: emailStats.deliveryRate,
        openRate: emailStats.openRate,
        clickRate: emailStats.clickRate
      }
    })

  } catch (error) {
    console.error('Admin stats error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
} 