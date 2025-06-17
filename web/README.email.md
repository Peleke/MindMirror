# Email Database Integration - TDD Plan (Updated for Supabase)

## Overview
Supabase-powered setup for MindMirror waitlist tracking with dual authentication layers:
- **Admin Auth**: Simple access for waitlist management
- **User Auth**: Foundation for future Next.js app (replacing Streamlit UI)

---

## Authentication Strategy

### 🔐 **Two-Tier Auth Architecture**

**1. Admin Level (Immediate Need)**
- Simple email/password auth for admin dashboard
- Access to subscriber management & analytics
- Uses Supabase Auth with admin role

**2. User Level (Future App)**
- Full user authentication for MindMirror app
- User profiles, journaling data, preferences
- Same Supabase Auth, different role/permissions

### 🏗️ **Supabase Setup Benefits**
- ✅ PostgreSQL database (no separate container needed)
- ✅ Built-in authentication & user management
- ✅ Row Level Security (RLS) for data isolation
- ✅ Real-time subscriptions (future use)
- ✅ Auto-generated TypeScript types
- ✅ Edge functions (for webhooks if needed)

---

## Phase 1: Supabase Setup

### ✅ **1.1 Install Dependencies**
```bash
npm install @supabase/supabase-js @supabase/auth-helpers-nextjs
npm install -D supabase # CLI tool
```

### ✅ **1.2 Supabase Project Setup**
1. Create project at [supabase.com](https://supabase.com)
2. Get project URL + anon key
3. Set up database schema in Supabase dashboard

### ✅ **1.3 Database Schema Design**
**Target Schema: `public` (Supabase default)**

```sql
-- Enable RLS on all tables
ALTER DATABASE postgres SET "app.jwt_secret" TO 'your-jwt-secret';

-- subscribers table (waitlist)
CREATE TABLE public.subscribers (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  source VARCHAR(50) DEFAULT 'landing_page',
  status VARCHAR(20) DEFAULT 'active',
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL -- for future user linking
);

-- email_events table (engagement tracking)
CREATE TABLE public.email_events (
  id BIGSERIAL PRIMARY KEY,
  subscriber_id BIGINT REFERENCES public.subscribers(id) ON DELETE CASCADE,
  email_id VARCHAR(255), -- Resend email ID
  event_type VARCHAR(50), -- sent, delivered, opened, clicked, bounced
  event_data JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- admin_users table (separate from regular users)
CREATE TABLE public.admin_users (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  role VARCHAR(50) DEFAULT 'admin',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Row Level Security policies
ALTER TABLE public.subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.email_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.admin_users ENABLE ROW LEVEL SECURITY;

-- Admin-only access policies
CREATE POLICY "Admins can view all subscribers" ON public.subscribers
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.admin_users 
      WHERE admin_users.user_id = auth.uid()
    )
  );

CREATE POLICY "Admins can view all email events" ON public.email_events
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.admin_users 
      WHERE admin_users.user_id = auth.uid()
    )
  );
```

### ✅ **1.4 Environment Variables**
```bash
# Add to .env.local
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
RESEND_API_KEY=re_your_resend_key
ADMIN_EMAIL=admin@yourdomain.com # First admin user
```

---

## Phase 2: Supabase Client & Auth Setup

### ✅ **2.1 Supabase Client Configuration**
**File: `lib/supabase/client.ts`**
- Browser client for client-side operations
- Server client for API routes
- Auth helpers for Next.js integration

### ✅ **2.2 Auth Middleware**
**File: `middleware.ts`**
- Route protection for admin pages
- Auth state management
- Redirect logic for unauthenticated users

### ✅ **2.3 Database Types**
**File: `lib/supabase/types.ts`**
- Auto-generated TypeScript types from Supabase
- Type-safe database operations

---

## Phase 3: Admin Authentication

### ✅ **3.1 Admin Login Page**
**File: `src/app/admin/login/page.tsx`**
- [ ] Simple email/password login form
- [ ] Supabase Auth integration
- [ ] Redirect to admin dashboard on success

### ✅ **3.2 Admin Layout & Protection**
**File: `src/app/admin/layout.tsx`**
- [ ] Check if user is authenticated admin
- [ ] Redirect non-admins to login
- [ ] Admin navigation sidebar

### ✅ **3.3 Admin User Management**
**File: `lib/supabase/admin.ts`**
- [ ] `createAdminUser(email, password)`
- [ ] `isUserAdmin(userId)`
- [ ] `getAdminProfile(userId)`

---

## Phase 4: Subscriber Management (Updated)

### ✅ **4.1 Update Subscription API**
**File: `src/app/api/subscribe/route.ts`**
- [ ] Use Supabase service role client
- [ ] Insert subscriber into database
- [ ] Handle duplicate emails gracefully
- [ ] Track email send event
- [ ] Store Resend email ID for tracking

### ✅ **4.2 Database Functions**
**File: `lib/supabase/subscribers.ts`**
- [ ] `createSubscriber(email, source)` 
- [ ] `getSubscriber(email)`
- [ ] `getAllSubscribers(page, limit)`
- [ ] `updateSubscriberStatus(id, status)`
- [ ] `getSubscriberStats()`

### ✅ **4.3 Email Event Tracking**
**File: `lib/supabase/email-events.ts`**
- [ ] `recordEmailEvent(subscriberId, emailId, eventType, data)`
- [ ] `getEmailStats(subscriberId)`
- [ ] `getOverallEmailStats()`

---

## Phase 5: Admin Dashboard (Auth-Protected)

### ✅ **5.1 Admin Dashboard Home**
**File: `src/app/admin/page.tsx`**
- [ ] Overview stats (total subscribers, recent signups)
- [ ] Quick actions (export, recent activity)
- [ ] Admin navigation

### ✅ **5.2 Subscribers Management**
**File: `src/app/admin/subscribers/page.tsx`**
- [ ] Authenticated table of all subscribers
- [ ] Real-time updates via Supabase subscriptions
- [ ] Search/filter functionality
- [ ] Pagination with URL state

### ✅ **5.3 Email Analytics Dashboard**
**File: `src/app/admin/analytics/page.tsx`**
- [ ] Email delivery metrics
- [ ] Engagement rates over time
- [ ] Recent email events feed

### ✅ **5.4 Admin API Routes (Protected)**
**File: `src/app/api/admin/`**
- [ ] `GET /api/admin/subscribers` - requires admin auth
- [ ] `GET /api/admin/stats` - email analytics
- [ ] `POST /api/admin/export` - CSV export

---

## Phase 6: Future User Auth Foundation

### ✅ **6.1 User Auth Components (Prep)**
**File: `components/auth/`**
- [ ] `LoginForm.tsx` - for future main app
- [ ] `SignupForm.tsx` - user registration
- [ ] `AuthProvider.tsx` - context wrapper

### ✅ **6.2 User Auth Hooks**
**File: `hooks/`**
- [ ] `useAuth()` - auth state management
- [ ] `useUser()` - user profile access
- [ ] `useAdmin()` - admin role checking

### ✅ **6.3 Protected Route Wrapper**
**File: `components/auth/ProtectedRoute.tsx`**
- [ ] HOC for protected pages
- [ ] Loading states during auth check
- [ ] Redirect logic

---

## Phase 7: Webhook Integration (Supabase Edge Functions or Next.js)

### ✅ **7.1 Resend Webhook Handler**
**File: `src/app/api/webhooks/resend/route.ts`**
- [ ] Verify webhook signature
- [ ] Use service role key for database writes
- [ ] Parse and store email events

### ✅ **7.2 Webhook Setup in Resend**
- [ ] Configure webhook URL in Resend dashboard
- [ ] Test webhook delivery with ngrok (development)

---

## Updated Implementation Order

1. **Setup Supabase project & schema** (45 min)
2. **Configure Supabase client & auth helpers** (30 min)
3. **Create admin auth flow** (45 min)
4. **Update subscribe API for Supabase** (30 min)
5. **Build admin dashboard with auth** (60 min)
6. **Add webhook handling** (30 min)
7. **Test full flow** (30 min)

**Total Estimated Time: ~4.5 hours** *(increased due to auth setup)*

---

## Success Criteria (Updated)

✅ **When complete, I should be able to:**
- Sign up with email on landing page → stored in Supabase
- Login to admin dashboard with Supabase Auth
- View protected subscriber list (admin-only)
- Track email delivery events via webhooks
- Have foundation ready for user authentication (future app)

✅ **Architecture supports:**
- Scalable admin access control
- Future transition from Streamlit to Next.js
- Real-time data updates
- Secure row-level access
- Production-ready user management

---

## Bonus: Docker Compose Not Needed! 🎉

Since we're using Supabase, we don't need a local PostgreSQL container. Supabase provides:
- Hosted PostgreSQL with web interface
- Built-in auth management
- Real-time subscriptions
- Automatic backups
- Edge functions (if needed)

This simplifies our development setup while giving us production-grade infrastructure.

---

*This updated plan sets us up for both immediate admin needs and future user authentication when we migrate from Streamlit to Next.js.* 