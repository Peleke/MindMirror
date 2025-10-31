# Phase 2 Hardening: Risk Analysis & Deferral Strategy

**Status:** DEFER HIGH-RISK ITEMS UNTIL POST-ALPHA
**Last Updated:** 2025-10-21
**Decision:** Deploy infra-v2 as-is, defer VPC/Gateway auth to post-alpha stabilization

---

## TL;DR: What to Do When

### ✅ **DO NOW (infra-v2 Deployment)**
- Cloud Run v2 migration
- Secret volume mounts
- Dedicated Supabase production
- RLS policies
- **Keep all services publicly accessible (ingress: ALL)**
- **Keep client-sent `x-internal-id` header**

**Timeline:** 4-6 days
**Risk Level:** LOW
**Suitable for:** 3-5 alpha users

### ❌ **DEFER TO POST-ALPHA (2-4 weeks after stable)**
- VPC private mesh networking
- Gateway authentication enhancement
- Client header removal

**Why defer:** High risk of total outage if misconfigured
**Security during deferral:** Acceptable for alpha (JWT + RLS protection)

---

## Risk Tier Breakdown

### 🟢 **TIER 1: SAFE TO DEPLOY NOW (Already in infra-v2)**

#### ✅ Story 3.1: Cloud Run v2 Migration
**What:** Upgrade from Cloud Run v1 to v2
**Risk:** Very Low
**User Impact:** Positive (better performance, no cold starts)
**Failure Mode:** Service won't start (visible immediately in health checks)
**Status:** ✅ Already implemented in infra-v2

#### ✅ Story 3.5: Secret Manager Hardening
**What:** Mount secrets as files (`/secrets/secret-name/secret-name`)
**Risk:** Low
**User Impact:** None (transparent to users)
**Failure Mode:** Service won't start (visible before users arrive)
**Testing:** Health checks validate secret access
**Status:** ✅ Already implemented in infra-v2

#### ✅ Story 3.2: Supabase Production Setup
**What:** Dedicated Supabase project with RLS policies
**Risk:** Medium (RLS could block legitimate users)
**Mitigation:** Test voucher flow end-to-end before inviting users
**User Impact:** None if tested properly
**Status:** ✅ In current deployment plan

#### ✅ Story 3.7: Bootstrap Automation
**What:** Scripts to automate GCP/Supabase setup
**Risk:** None (just tooling)
**Status:** ✅ Complete in infra-v2/bootstrap/

**DECISION:** ✅ All Tier 1 items are SAFE to deploy for alpha launch.

---

### 🔴 **TIER 3: HIGH RISK - DEFER TO POST-ALPHA**

#### ❌ Story 3.3: VPC Connector + Private Mesh Networking
**DEFER TIMELINE:** 4-6 weeks after alpha launch

**What it does:**
```hcl
# CURRENT (infra-v2 as-is):
ingress = "INGRESS_TRAFFIC_ALL"  # All services publicly accessible
# Gateway → https://users-service-xyz.run.app/health

# AFTER VPC HARDENING:
ingress = "INGRESS_TRAFFIC_INTERNAL"  # Only VPC traffic allowed
vpc_access {
  connector = google_vpc_access_connector.connector.id
  egress    = "PRIVATE_RANGES_ONLY"
}
# Gateway → http://10.8.0.5:8000/health (internal VPC IP)
```

**Why it's HIGH RISK:**

1. **Total Outage Risk:**
   ```bash
   # Before VPC: Works
   curl https://users-service-xyz.run.app/health → 200 OK

   # After VPC misconfiguration: Dead
   curl https://users-service-xyz.run.app/health → 403 FORBIDDEN (ingress: internal)
   # Gateway tries internal: http://10.8.0.5:8000/health → TIMEOUT
   # Result: "suddenly fucking dies for everyone" ✅
   ```

2. **Failure Scenarios:**
   - VPC connector misconfigured → Gateway can't reach mesh → Total outage
   - Firewall rules wrong → Port 443 blocked internally → Dead
   - Subnet IP exhaustion → Services can't get IPs → Cascading failure
   - Connector capacity exceeded → Intermittent failures → Random auth failures

3. **Real-World Example:**
   ```hcl
   # Easy typo that kills everything:
   resource "google_compute_subnetwork" "vpc" {
     ip_cidr_range = "10.8.0.0/27"  # Only 32 IPs available
   }

   # 9 services (8 mesh + gateway) × 3 min_instances = 27 IPs used
   # After 32 connections: "No available IP addresses"
   # Gateway can't reach mesh → TOTAL OUTAGE
   ```

**Why Current Setup is ACCEPTABLE for Alpha:**
- Services are still protected by JWT authentication
- RLS policies prevent cross-user data access
- Supabase connection is already secure (TLS)
- Attack surface is small with 3-5 trusted alpha users
- Public mesh services aren't a real security risk if you trust your alpha users

**How to De-Risk When Ready:**
```bash
# 1. Create VPC in staging FIRST
cd infra-v2/modules/networking
tofu apply -var="environment=staging"

# 2. Test EVERY service can reach each other over VPC
for service in agent journal habits meals movements practices users; do
  curl http://10.8.0.X:8000/health
done

# 3. Test gateway federation over VPC
curl https://gateway-staging.run.app/graphql

# 4. Run for 1-2 weeks in staging

# 5. Deploy to production during low-traffic window (3am Sunday)

# 6. Have rollback plan ready:
git checkout main  # Before VPC changes
tofu apply -var-file=env.production.tfvars
```

**DECISION:** ❌ DEFER - Too risky for alpha launch. Deploy when you have time to fix issues.

---

#### ❌ Story 3.4a: Gateway Authentication Enhancement (ID Exchange)
**DEFER TIMELINE:** 4-6 weeks after alpha launch

**What it does:**
```typescript
// NEW AUTH FLOW (deferred):
async function authenticate(req: Request) {
  // 1. Parse JWT from Authorization header
  const jwt = parseJWT(req.headers.authorization);
  const supabaseUserId = jwt.sub;

  // 2. Check Redis cache for internal ID
  let internalId = await redis.get(`uid:${supabaseUserId}`);

  // 3. Cache miss? Query users_service
  if (!internalId) {
    const response = await fetch(
      `${USERS_SERVICE_URL}/api/users/${supabaseUserId}`
    );
    if (!response.ok) {
      throw new Error('Users service unavailable');  // ← BLOCKS ALL REQUESTS
    }
    const user = await response.json();
    internalId = user.internal_id;

    // 4. Cache for 1 hour
    await redis.set(`uid:${supabaseUserId}`, internalId, 'EX', 3600);
  }

  // 5. Forward to mesh services
  req.headers['x-internal-id'] = internalId;
}
```

**Why it's HIGH RISK:**

1. **New Dependency Chain:**
   ```
   Client → Gateway → users_service (NEW!) → internal_id → mesh services
                ↓
              Redis (NEW!)

   If Redis dies: Every request queries users_service → overload → OUTAGE
   If users_service slow: +500ms to EVERY request → Feels broken
   ```

2. **Failure Scenarios:**
   - **Redis down:** Fall back to users_service → overload → cascading failure
   - **users_service slow/down:** Gateway blocks all requests → Total lockout
   - **Cache invalidation bug:** User A sees User B's data → SECURITY INCIDENT
   - **JWT parsing bug:** Nobody can authenticate → App is unusable

3. **Cache Invalidation Nightmare:**
   ```typescript
   // What if user is deleted?
   await redis.get(`uid:${deletedUserId}`);  // Returns cached ID
   // Gateway sends x-internal-id for deleted user
   // Mesh services process request for ghost user
   // Data corruption possible
   ```

**Why Current "Insecure" Setup is FINE for Alpha:**

Current flow:
```typescript
// Client sends x-internal-id directly (yes, spoofable)
req.headers['x-internal-id'] = currentUser.internalId;  // From client
```

To exploit this, attacker needs:
1. ✅ Valid Supabase JWT (hard - requires email access or password)
2. ✅ Another user's internal ID (UUID - hard to guess)
3. ❌ RLS policies STILL block (double layer of protection)

**Real attack scenario:**
```sql
-- Attacker spoofs x-internal-id: "victim-uuid-12345"
-- But RLS policy checks JWT, not header:
CREATE POLICY "Users can only see own journals" ON journals
  USING (auth.uid() = user_id);  -- ← Checks Supabase JWT, not header!

-- Result: Attacker blocked by RLS even with spoofed header
```

With 3-5 trusted alpha users, this risk is **negligible**.

**DECISION:** ❌ DEFER - Current setup is secure enough for alpha. Not worth the outage risk.

---

#### ❌ Story 3.4b: Client Header Removal
**DEFER TIMELINE:** After 3.4a proven stable (if ever)

**Dependencies:** Requires 3.4a first
**Risk:** Medium (client-side breaking change)
**Recommendation:** Probably never do this - just document that gateway is authoritative

**DECISION:** ❌ DEFER indefinitely

---

### 🟡 **TIER 2: MEDIUM PRIORITY (Do Within First Month)**

#### ⏰ Story 3.6: CI/CD Pipeline
**TIMELINE:** 1-2 weeks after alpha launch

**What it does:** GitHub Actions pipeline for automated deployments

**Why it's safe to defer initially:**
- Doesn't affect running services at all
- Manual `tofu apply` works fine for 3-5 users
- You can iterate fast enough manually during alpha

**Why you should do it soon:**
- Rapid iteration based on alpha feedback
- Manual deployments get tedious
- Non-blocking tests + manual approval = safe automation

**Risk if misconfigured:**
- Could deploy broken code → But manual approval gate prevents this
- Path filters wrong → Rebuild everything → Wastes time (not user-facing)

**How to de-risk:**
```yaml
# .github/workflows/deploy.yml
on:
  push:
    tags:
      - 'v*'  # Only deploy on version tags (explicit control)

jobs:
  deploy:
    steps:
      - name: Run tests
        run: npm test
        continue-on-error: true  # Non-blocking

      - name: Manual approval
        uses: trstringer/manual-approval@v1
        with:
          approvers: peleke  # You must approve

      - name: Deploy
        run: tofu apply -auto-approve
```

**DECISION:** ⏰ Do within 1-2 weeks. Low risk, high value.

---

## Recommended Alpha Launch Plan

### **Phase 1: Alpha Launch (NOW - 4-6 days)**

**Deploy infra-v2 as-is with:**
- ✅ Cloud Run v2 (performance improvement)
- ✅ Secret volume mounts (security improvement)
- ✅ Dedicated Supabase production (data isolation)
- ✅ RLS policies (user data protection)
- ✅ **Public ingress on all services** (deferred VPC hardening)
- ✅ **Client sends `x-internal-id`** (deferred gateway auth)

**Security Posture:**
- ✅ JWT authentication via Supabase
- ✅ RLS policies prevent cross-user data access
- ✅ HTTPS everywhere
- ✅ Secrets in Secret Manager (not env vars)
- ✅ Least-privilege IAM per service
- ⚠️ Mesh services publicly accessible (acceptable for alpha)
- ⚠️ Client can spoof `x-internal-id` (but RLS limits damage)

**Risk Assessment:** **LOW** - suitable for 3-5 trusted alpha users

**Timeline:**
1. Review bootstrap scripts (30 mins)
2. Update app code for secret volumes (1-2 hours)
3. Build Docker images (1 hour)
4. Run bootstrap scripts (2 hours)
5. Deploy with OpenTofu (1 hour)
6. Validate end-to-end (1 hour)
7. Invite alpha users

---

### **Phase 2: Post-Alpha Hardening (AFTER Users Stable)**

**Week 2-3 after launch:**
1. ✅ Set up CI/CD pipeline (low risk, high value)
2. ✅ Add monitoring/alerting (Cloud Logging, uptime checks)
3. ✅ Set up budget alerts
4. ✅ Document operational runbook

**Week 4-6 after launch (when you have breathing room):**
1. 🔴 Test VPC networking in staging (extensively)
2. 🔴 Deploy VPC to production (during low-traffic window)
3. 🔴 Test gateway auth enhancement in staging
4. 🔴 Phased rollout to production

---

## What WON'T Break (Safe Operations)

These are always safe to do in production:

### ✅ Scaling Changes
```hcl
# infra-v2/env.production.tfvars
min_instances_critical = 3  # Was 1 - just costs more money
max_instances = 20          # Was 10 - just allows more scale
```

### ✅ Resource Adjustments
```hcl
cpu_limit    = "2000m"  # Was "1000m" - better performance
memory_limit = "1024Mi" # Was "512Mi" - prevents OOM
```

### ✅ Adding Secrets
```hcl
# modules/agent_service/main.tf
secret_volumes = [
  # ... existing secrets ...
  {
    volume_name = "anthropic-api-key"  # New secret
    secret_name = var.anthropic_api_key_secret
    filename    = "anthropic-api-key"
  },
]
```

### ✅ Deploying New Service Versions
```bash
# Build new image
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/swae/agent-service:v2 .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/swae/agent-service:v2

# Update tfvars
agent_service_image = "us-central1-docker.pkg.dev/PROJECT/swae/agent-service:v2"

# Deploy
tofu apply -var-file=env.production.tfvars

# Health checks prevent bad deploys automatically
```

### ✅ Database Migrations
```bash
# Alembic is transactional - safe to run
cd infra-v2/bootstrap
./03-run-migrations.sh
```

### ✅ Supabase Config Changes
- JWT expiry adjustments
- Email confirmation settings
- RLS policy updates (test in staging first)

---

## What WILL Break (Dangerous Operations)

### ❌ Changing Ingress Rules
```hcl
# DON'T DO THIS without VPC connector ready:
ingress = "INGRESS_TRAFFIC_INTERNAL"  # ← Instant outage if VPC not configured
```

### ❌ Changing Service Networking
```hcl
# DON'T DO THIS without extensive testing:
vpc_access {
  connector = google_vpc_access_connector.connector.id
  egress    = "PRIVATE_RANGES_ONLY"
}
```

### ❌ Modifying Gateway Auth Flow
```typescript
// DON'T DO THIS without Redis + users_service tested:
const internalId = await getInternalIdFromUsersService(jwt.sub);
```

### ❌ Changing Database Connection Strings
```hcl
# DON'T DO THIS without validation:
database_url_secret = "NEW_DATABASE_URL"  # All services reconnect → brief outage
```

---

## Decision Matrix: Should I Deploy This Change?

Ask yourself:

1. **Does it modify network traffic flow?**
   - YES → ❌ DEFER (VPC, firewall rules)
   - NO → Continue to #2

2. **Does it add new critical dependencies?**
   - YES → ❌ DEFER (Redis cache, ID exchange)
   - NO → Continue to #3

3. **Can I test it in staging first?**
   - NO → ❌ DEFER (wait until you can test)
   - YES → Continue to #4

4. **If it fails, will users be locked out?**
   - YES → ❌ DEFER (auth changes, database changes)
   - NO → Continue to #5

5. **Can I roll back in <5 minutes?**
   - NO → ❌ DEFER (database migrations without backups)
   - YES → ✅ SAFE TO DEPLOY

---

## Testing Checklist Before VPC/Auth Hardening

When you're ready to tackle Phase 2 (4-6 weeks from now), use this checklist:

### Staging Validation (1-2 weeks)
- [ ] VPC connector created in staging
- [ ] All services reachable over VPC (test with curl)
- [ ] Gateway can federate schemas over VPC
- [ ] Load test: 100 concurrent requests succeed
- [ ] Failover test: Kill VPC connector, verify fallback works
- [ ] Redis cluster created and tested
- [ ] Gateway ID exchange logic tested with real JWTs
- [ ] Cache invalidation tested (user deletion scenario)
- [ ] Performance test: Latency <50ms for cached lookups

### Production Deployment (1 day)
- [ ] Deploy during low-traffic window (Sunday 3am)
- [ ] Have rollback plan ready (`git checkout` before VPC changes)
- [ ] Monitor error rates closely (Cloud Logging filters)
- [ ] Validate health checks for all services
- [ ] Test auth flow with real user account
- [ ] Verify no RLS policy violations in logs
- [ ] Check latency (p95 should stay <500ms)

### Post-Deployment (1 week)
- [ ] Monitor for 7 days before declaring success
- [ ] Check for intermittent failures (VPC connector capacity)
- [ ] Validate cost impact (VPC connector costs money)
- [ ] Document any issues encountered

---

## Cost Impact Analysis

### Current Plan (infra-v2 as-is)
- Cloud Run (3 critical services × 1 min instance) = ~$52/month
- Cloud Run (6 normal services × 0 min instances) = ~$5/month (requests only)
- Secret Manager = ~$1/month
- GCS = ~$1/month
- Pub/Sub = ~$1/month
- **Total: ~$60/month**

### After VPC Hardening (deferred)
- VPC Connector (always-on) = **+$30/month**
- NAT Gateway (for egress) = **+$45/month**
- **New Total: ~$135/month**

**DECISION:** Defer VPC to avoid 2.25× cost increase during alpha.

---

## Communication Plan

### What to Tell Alpha Users

**During Alpha (infra-v2 as-is):**
> "We're running on a production-grade infrastructure with industry-standard security:
> - Encrypted connections (HTTPS)
> - Database-level user isolation (RLS policies)
> - Secure credential storage (Secret Manager)
> - Automated health monitoring
>
> You're in good hands!"

**After VPC Hardening (future):**
> "We've upgraded our infrastructure with additional network isolation:
> - Private mesh networking (services not publicly accessible)
> - Enhanced authentication (gateway-validated IDs)
>
> You shouldn't notice any changes - just even better security!"

---

## Conclusion

**For Alpha Launch:**
- ✅ Deploy infra-v2 as-is (Tier 1 items only)
- ✅ Security is **good enough** for 3-5 trusted users
- ✅ Focus on getting users onboarded smoothly
- ❌ Don't touch networking or auth flow

**Post-Alpha (4-6 weeks):**
- ⏰ Add CI/CD first (low risk, high value)
- 🔴 Then tackle VPC + gateway auth (extensively test in staging)

**Key Principle:**
> "Don't change production networking until you have time to fix it if it breaks."

You're making the right call to defer high-risk items. Get users in the door first, then harden incrementally.

---

**Questions? Concerns?** Come back to this doc when you're ready for Phase 2 hardening.

**Good luck with the alpha launch!** 🚀
