import { createServiceRoleClient } from './server'
import { Database } from './types'

type Subscriber = Database['waitlist']['Tables']['subscribers']['Row']
type EmailEvent = Database['waitlist']['Tables']['email_events']['Row']

// Create a new subscriber
export async function createSubscriber(email: string, source: string = 'landing_page'): Promise<{ subscriber: Subscriber | null; error: any }> {
  const supabase = createServiceRoleClient()
  
  try {
    const { data, error } = await supabase
      .from('subscribers')
      .insert([{
        email: email.toLowerCase(),
        source,
        status: 'active'
      }])
      .select()
      .single()

    return { subscriber: data, error }
  } catch (error) {
    return { subscriber: null, error }
  }
}

// Get subscriber by email
export async function getSubscriber(email: string): Promise<Subscriber | null> {
  const supabase = createServiceRoleClient()
  
  try {
    const { data, error } = await supabase
      .from('subscribers')
      .select('*')
      .eq('email', email.toLowerCase())
      .single()

    return error ? null : data
  } catch (error) {
    return null
  }
}

// Get all subscribers with pagination
export async function getAllSubscribers(page: number = 1, limit: number = 50): Promise<{ subscribers: Subscriber[]; total: number; error: any }> {
  const supabase = createServiceRoleClient()
  
  try {
    const offset = (page - 1) * limit

    // Get total count
    const { count, error: countError } = await supabase
      .from('subscribers')
      .select('*', { count: 'exact', head: true })

    if (countError) {
      return { subscribers: [], total: 0, error: countError }
    }

    // Get paginated data
    const { data, error } = await supabase
      .from('subscribers')
      .select('*')
      .order('subscribed_at', { ascending: false })
      .range(offset, offset + limit - 1)

    return { 
      subscribers: data || [], 
      total: count || 0, 
      error: null 
    }
  } catch (error) {
    return { subscribers: [], total: 0, error }
  }
}

// Update subscriber status
export async function updateSubscriberStatus(id: number, status: string): Promise<{ subscriber: Subscriber | null; error: any }> {
  const supabase = createServiceRoleClient()
  
  try {
    const { data, error } = await supabase
      .from('subscribers')
      .update({ status })
      .eq('id', id)
      .select()
      .single()

    return { subscriber: data, error }
  } catch (error) {
    return { subscriber: null, error }
  }
}

// Get subscriber statistics
export async function getSubscriberStats(): Promise<{
  total: number
  active: number
  recentSignups: number // last 7 days
  error: any
}> {
  const supabase = createServiceRoleClient()
  
  try {
    // Get total count
    const { count: total, error: totalError } = await supabase
      .from('subscribers')
      .select('*', { count: 'exact', head: true })

    if (totalError) {
      return { total: 0, active: 0, recentSignups: 0, error: totalError }
    }

    // Get active count
    const { count: active, error: activeError } = await supabase
      .from('subscribers')
      .select('*', { count: 'exact', head: true })
      .eq('status', 'active')

    if (activeError) {
      return { total: total || 0, active: 0, recentSignups: 0, error: activeError }
    }

    // Get recent signups (last 7 days)
    const sevenDaysAgo = new Date()
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)

    const { count: recentSignups, error: recentError } = await supabase
      .from('subscribers')
      .select('*', { count: 'exact', head: true })
      .gte('subscribed_at', sevenDaysAgo.toISOString())

    if (recentError) {
      return { total: total || 0, active: active || 0, recentSignups: 0, error: recentError }
    }

    return {
      total: total || 0,
      active: active || 0,
      recentSignups: recentSignups || 0,
      error: null
    }
  } catch (error) {
    return { total: 0, active: 0, recentSignups: 0, error }
  }
}

// Record email event
export async function recordEmailEvent(
  subscriberId: number, 
  emailId: string | null, 
  eventType: string, 
  data: any = null
): Promise<{ event: EmailEvent | null; error: any }> {
  const supabase = createServiceRoleClient()
  
  try {
    const { data: eventData, error } = await supabase
      .from('email_events')
      .insert([{
        subscriber_id: subscriberId,
        email_id: emailId,
        event_type: eventType,
        event_data: data
      }])
      .select()
      .single()

    return { event: eventData, error }
  } catch (error) {
    return { event: null, error }
  }
}

// Get email statistics for a subscriber
export async function getEmailStats(subscriberId: number): Promise<{
  sent: number
  delivered: number
  opened: number
  clicked: number
  error: any
}> {
  const supabase = createServiceRoleClient()
  
  try {
    const { data, error } = await supabase
      .from('email_events')
      .select('event_type')
      .eq('subscriber_id', subscriberId)

    if (error) {
      return { sent: 0, delivered: 0, opened: 0, clicked: 0, error }
    }

    const stats = {
      sent: 0,
      delivered: 0,
      opened: 0,
      clicked: 0,
      error: null
    }

    data?.forEach(event => {
      switch (event.event_type) {
        case 'sent':
          stats.sent++
          break
        case 'delivered':
          stats.delivered++
          break
        case 'opened':
          stats.opened++
          break
        case 'clicked':
          stats.clicked++
          break
      }
    })

    return stats
  } catch (error) {
    return { sent: 0, delivered: 0, opened: 0, clicked: 0, error }
  }
}

// Get overall email statistics
export async function getOverallEmailStats(): Promise<{
  totalEmails: number
  deliveryRate: number
  openRate: number
  clickRate: number
  error: any
}> {
  const supabase = createServiceRoleClient()
  
  try {
    const { data, error } = await supabase
      .from('email_events')
      .select('event_type')

    if (error) {
      return { totalEmails: 0, deliveryRate: 0, openRate: 0, clickRate: 0, error }
    }

    const stats = {
      sent: 0,
      delivered: 0,
      opened: 0,
      clicked: 0
    }

    data?.forEach(event => {
      switch (event.event_type) {
        case 'sent':
          stats.sent++
          break
        case 'delivered':
          stats.delivered++
          break
        case 'opened':
          stats.opened++
          break
        case 'clicked':
          stats.clicked++
          break
      }
    })

    return {
      totalEmails: stats.sent,
      deliveryRate: stats.sent > 0 ? (stats.delivered / stats.sent) * 100 : 0,
      openRate: stats.delivered > 0 ? (stats.opened / stats.delivered) * 100 : 0,
      clickRate: stats.opened > 0 ? (stats.clicked / stats.opened) * 100 : 0,
      error: null
    }
  } catch (error) {
    return { totalEmails: 0, deliveryRate: 0, openRate: 0, clickRate: 0, error }
  }
} 