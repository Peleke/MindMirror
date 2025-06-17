export interface Database {
  public: {
    Tables: {
      [_ in never]: never
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
  waitlist: {
    Tables: {
      subscribers: {
        Row: {
          id: number
          email: string
          subscribed_at: string
          source: string
          status: string
          user_id: string | null
        }
        Insert: {
          id?: number
          email: string
          subscribed_at?: string
          source?: string
          status?: string
          user_id?: string | null
        }
        Update: {
          id?: number
          email?: string
          subscribed_at?: string
          source?: string
          status?: string
          user_id?: string | null
        }
      }
      email_events: {
        Row: {
          id: number
          subscriber_id: number
          email_id: string | null
          event_type: string
          event_data: any | null
          created_at: string
        }
        Insert: {
          id?: number
          subscriber_id: number
          email_id?: string | null
          event_type: string
          event_data?: any | null
          created_at?: string
        }
        Update: {
          id?: number
          subscriber_id?: number
          email_id?: string | null
          event_type?: string
          event_data?: any | null
          created_at?: string
        }
      }
      admin_users: {
        Row: {
          id: number
          user_id: string
          role: string
          created_at: string
        }
        Insert: {
          id?: number
          user_id: string
          role?: string
          created_at?: string
        }
        Update: {
          id?: number
          user_id?: string
          role?: string
          created_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
}

export type Subscriber = Database['waitlist']['Tables']['subscribers']['Row']
export type EmailEvent = Database['waitlist']['Tables']['email_events']['Row']
export type AdminUser = Database['waitlist']['Tables']['admin_users']['Row'] 