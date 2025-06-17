# MindMirror Waitlist Architecture

## Overview
Complete waitlist management system using dedicated `waitlist` schema in Supabase with admin dashboard and email tracking.

## 🏗️ Schema Structure

### `waitlist.subscribers`
Core subscriber management table:
- `id` - Auto-incrementing primary key
- `email` - Unique email address (lowercase)
- `subscribed_at` - Timestamp with timezone
- `source` - Where they signed up (default: 'landing_page')
- `status` - Subscription status (default: 'active')
- `user_id` - Future link to auth.users for full app migration

### `waitlist.email_events`
Email engagement tracking:
- `id` - Auto-incrementing primary key
- `subscriber_id` - References waitlist.subscribers
- `email_id` - Resend email ID for tracking
- `event_type` - sent, delivered, opened, clicked, bounced, failed
- `event_data` - JSONB for additional event metadata
- `created_at` - Event timestamp

### `waitlist.admin_users`
Admin access control:
- `id` - Auto-incrementing primary key
- `user_id` - References auth.users
- `role` - Admin role (default: 'admin')
- `created_at` - Admin creation timestamp

## 🔐 Security & Permissions

### Row Level Security (RLS)
All tables have RLS enabled with admin-only policies:
- Only users in `waitlist.admin_users` can access data
- Service role bypasses RLS for API operations

### Schema Permissions
- `authenticated` and `service_role` have USAGE on schema
- `service_role` has ALL permissions on tables and sequences

## 🎯 API Endpoints

### Public Endpoints
- `POST /api/subscribe` - Email capture with Supabase storage
- `POST /api/admin/setup` - Create first admin user

### Protected Admin Endpoints
- `POST /api/admin/verify` - Check admin privileges
- Admin dashboard routes (middleware protected)

## 📁 File Structure

```
lib/supabase/
├── client.ts          # Browser Supabase client
├── server.ts          # Server Supabase client + service role
├── types.ts           # TypeScript schema definitions
├── admin.ts           # Admin user management functions
└── subscribers.ts     # Subscriber & email event functions

src/app/
├── admin/
│   ├── login/page.tsx      # Admin login form
│   ├── page.tsx            # Protected admin route
│   └── AdminDashboard.tsx  # Admin UI component
└── api/
    ├── subscribe/route.ts      # Email capture + DB storage
    └── admin/
        ├── setup/route.ts      # First admin creation
        └── verify/route.ts     # Admin privilege check

middleware.ts          # Route protection
```

## 🔄 Data Flow

### Email Capture Flow
1. User submits email on landing page
2. `POST /api/subscribe` validates and stores in `waitlist.subscribers`
3. Sends welcome email via Resend
4. Records email event in `waitlist.email_events`
5. Returns success response

### Admin Access Flow
1. Admin visits `/admin/login`
2. Middleware checks authentication
3. Login form calls Supabase auth
4. API verifies admin status via `waitlist.admin_users`
5. Redirects to protected admin dashboard

## 🚀 Ready for Scale

### Future App Migration
- `user_id` field ready to link subscribers to full app users
- Admin auth separate from user auth (no conflicts)
- Schema isolation keeps waitlist data organized

### Email Webhook Integration
- Email events table ready for Resend webhook data
- Event tracking supports engagement analytics
- Extensible JSONB event_data for future metrics

### Admin Dashboard Expansion
- Subscriber helper functions ready for management UI
- Statistics functions for analytics dashboard
- Permission system ready for role-based access

## 🛠️ Setup Commands

```bash
# 1. Install dependencies (already done)
npm install @supabase/supabase-js @supabase/ssr

# 2. Run schema SQL in Supabase (see SUPABASE_SETUP.md)

# 3. Create first admin
curl -X POST http://localhost:3000/api/admin/setup \
  -H "Content-Type: application/json" \
  -d '{"email": "peleke.s@protonmail.com", "password": "password"}'

# 4. Test full flow
# - Visit /landing and sign up
# - Check Supabase waitlist schema for data
# - Login at /admin/login
# - View admin dashboard
```

## ✅ What Works Now
- ✅ Email capture stores to `waitlist.subscribers`
- ✅ Email events tracked in `waitlist.email_events`
- ✅ Admin authentication with role checking
- ✅ Protected admin dashboard
- ✅ Row-level security and permissions
- ✅ Type-safe database operations
- ✅ Organized schema separation

## 🎯 Next Phase Ready
- Subscriber management UI
- Email analytics dashboard
- Webhook handlers for real-time events
- CSV export functionality
- Advanced admin features

Perfect foundation for a production-ready waitlist system! 🎉 