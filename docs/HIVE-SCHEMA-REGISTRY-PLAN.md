# GraphQL Hive Schema Registry Integration Plan

**Status**: Planning (Slow-burn optimization alongside user onboarding)
**Priority**: Medium (After GitOps validation)
**Owner**: DevOps/Backend
**Created**: 2025-10-27
**Last Updated**: 2025-10-27

---

## Quick Reference: Manual Gateway Management (Current Runbook)

**Until Hive is implemented, use this workflow for gateway updates:**

### When Gateway Auto-Rebuilds ✅

Gateway rebuilds automatically via CI/CD when:
- ✅ Files in `mesh/*` change (config, Dockerfile, package.json)
- ✅ Files in `gateway/*` change
- ✅ Any Dockerfile changes

**No manual action needed** - just merge your PR!

### When to Manually Rebuild Gateway 🔧

Gateway does NOT auto-rebuild for:
- ❌ Service schema changes (e.g., journal adds new GraphQL field)
- ❌ Service-only deployments (agent updates but gateway unchanged)

**Manual rebuild options:**

#### Option 1: Force CI/CD Rebuild (Recommended)
```bash
# Add a rebuild trigger to force CI/CD to rebuild gateway
echo "# Rebuild triggered: $(date)" >> mesh/.rebuild-trigger
git add mesh/.rebuild-trigger
git commit -m "chore: rebuild gateway for schema updates"
git push

# CI/CD detects mesh/* change → rebuilds gateway automatically
```

#### Option 2: Manual Build & Deploy
```bash
# 1. Build gateway with updated supergraph
docker build -t us-east4-docker.pkg.dev/mindmirror-69/mindmirror/mesh:manual-$(date +%Y%m%d) \
  -f mesh/Dockerfile mesh/
docker push us-east4-docker.pkg.dev/mindmirror-69/mindmirror/mesh:manual-$(date +%Y%m%d)

# 2. Quick deploy (bypass Terraform)
gcloud run deploy gateway \
  --image us-east4-docker.pkg.dev/mindmirror-69/mindmirror/mesh:manual-$(date +%Y%m%d) \
  --project mindmirror-69 \
  --region us-east4

# 3. Or update tfvars (proper way)
# Edit infra/staging.auto.tfvars:
gateway_image = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/mesh:manual-$(date +%Y%m%d)"
# Then: cd infra && tofu apply -var-file=staging.auto.tfvars
```

#### Option 3: Do Nothing (Lazy/On-Demand)
```bash
# If schema changes are additive (no breaking changes):
# - Services deploy with new schemas
# - Gateway keeps working with old supergraph
# - Rebuild gateway when next `mesh/*` change happens naturally
#
# Good for: Development, non-critical additions
```

### Staging vs Production

**Staging** (mindmirror-69):
```bash
gcloud run deploy gateway \
  --image us-east4-docker.pkg.dev/mindmirror-69/mindmirror/mesh:TAG \
  --project mindmirror-69 \
  --region us-east4
```

**Production** (mindmirror-prod):
```bash
gcloud run deploy gateway \
  --image us-east4-docker.pkg.dev/mindmirror-prod/mindmirror/mesh:TAG \
  --project mindmirror-prod \
  --region us-east4
```

### When Hive is Ready

This manual workflow becomes obsolete. Gateway will:
- ✅ Auto-fetch latest supergraph from Hive CDN
- ✅ No rebuilds needed for schema changes
- ✅ Always up-to-date with latest service schemas

---

## Problem Statement

### Current Architecture Issues

**Local Development (✅ Works Great)**:
```
GraphQL Services → mesh-compose → build/supergraph.graphql → gateway → Clients
```

**Production Deployment (❌ Broken)**:
1. When a GraphQL service schema changes, the service deploys successfully
2. BUT the gateway still has the old supergraph baked into its Docker image
3. Gateway has no way to discover schema changes
4. Can't introspect live Cloud Run services from GitHub Actions (no network access)
5. Result: **Stale schemas in production**

### Critical Gaps

1. **No Schema Publishing**: Services don't publish their GraphQL schemas anywhere
2. **No Supergraph Re-composition**: Supergraph is baked into gateway at build time
3. **No Schema Registry**: No centralized schema storage or version tracking
4. **No Dependency Detection**: `changed-services.sh` doesn't detect schema-only changes
5. **No Breaking Change Detection**: No validation before deployment

---

## Proposed Solution: GraphQL Hive Cloud

**GraphQL Hive** is an open-source schema registry and gateway management platform from The Guild.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ CI/CD Pipeline (GitHub Actions)                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Service Code Change → Build & Deploy → Publish Schema     │
│                                             ↓               │
│                                    hive schema:publish      │
│                                             ↓               │
└─────────────────────────────────────────────┬───────────────┘
                                              │
                                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Hive Cloud (SaaS)                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Receives schema from service                           │
│  2. Validates federation compatibility                     │
│  3. Detects breaking changes                               │
│  4. Auto-composes supergraph                               │
│  5. Publishes to Cloudflare CDN                            │
│                                                             │
└─────────────────────────────────────────────┬───────────────┘
                                              │
                                              ↓ HTTPS/CDN
┌─────────────────────────────────────────────────────────────┐
│ Production (Cloud Run)                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Gateway fetches supergraph from CDN on startup            │
│  OR polls periodically for updates                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Benefits

1. ✅ **Automatic Schema Publishing**: Each service publishes schema after deployment
2. ✅ **Automatic Supergraph Composition**: Hive composes federation automatically
3. ✅ **Breaking Change Detection**: Catches issues before production
4. ✅ **High-Availability CDN**: Cloudflare-backed supergraph distribution
5. ✅ **No Network Requirements**: Gateway pulls from CDN, doesn't introspect services
6. ✅ **Schema Versioning**: Full history of schema changes
7. ✅ **Free Tier**: 1M checks/month, unlimited operations, 7 targets
8. ✅ **No Breaking Changes**: Add incrementally alongside existing system

---

## Implementation Phases

### Phase 1: Hive Cloud Setup (One-Time, ~1 hour)

**Tasks**:

1. **Create Hive Account**
   - Visit: https://app.graphql-hive.com
   - Sign up with GitHub OAuth
   - Free tier (no credit card required)

2. **Create Organization**
   - Name: `mindmirror`

3. **Create Projects**
   - `staging` (for staging environment)
   - `production` (for production environment)

4. **Create Targets** (per project)

   For **staging** project:
   - `journal` - Journal service GraphQL schema
   - `agent` - Agent service GraphQL schema
   - `habits` - Habits service GraphQL schema
   - `meals` - Meals service GraphQL schema
   - `movements` - Movements service GraphQL schema
   - `practices` - Practices service GraphQL schema
   - `users` - Users service GraphQL schema

   For **production** project:
   - Same 7 targets as staging

5. **Generate Access Tokens**

   Create the following tokens:
   - `HIVE_STAGING_TOKEN` - Publish access for staging targets
   - `HIVE_PRODUCTION_TOKEN` - Publish access for production targets
   - `HIVE_CDN_KEY` - CDN access for gateway to fetch supergraph
   - `HIVE_STAGING_CDN_ENDPOINT` - CDN URL for staging supergraph
   - `HIVE_PRODUCTION_CDN_ENDPOINT` - CDN URL for production supergraph

6. **Add Secrets to GitHub**

   Add as **Repository Secrets** (not environment secrets):
   ```bash
   gh secret set HIVE_STAGING_TOKEN
   gh secret set HIVE_PRODUCTION_TOKEN
   gh secret set HIVE_CDN_KEY
   gh secret set HIVE_STAGING_CDN_ENDPOINT
   gh secret set HIVE_PRODUCTION_CDN_ENDPOINT
   ```

**Deliverables**:
- [ ] Hive account created
- [ ] Organization + projects + targets configured
- [ ] Access tokens generated
- [ ] GitHub secrets configured
- [ ] Documentation updated with Hive URLs

---

### Phase 2: Schema Export Utility (Dev Tooling, ~2 hours)

**Problem**: Services don't currently expose their schemas as standalone files.

**Solution**: Create utility to extract GraphQL SDL from running services.

**Implementation**:

1. **Create Schema Export Script**

   ```python
   # scripts/export-schema.py
   """Extract GraphQL SDL from running service via introspection."""
   import requests
   import sys
   from graphql import build_client_schema, get_introspection_query, print_schema

   def export_schema(service_url: str, output_file: str):
       """
       Introspect GraphQL service and export SDL.

       Args:
           service_url: Base URL of service (e.g., https://journal-xyz.run.app)
           output_file: Path to write schema.graphql
       """
       introspection_query = get_introspection_query()

       response = requests.post(
           f"{service_url}/graphql",
           json={"query": introspection_query},
           headers={"Content-Type": "application/json"}
       )
       response.raise_for_status()

       introspection_result = response.json()['data']
       schema = build_client_schema(introspection_result)
       sdl = print_schema(schema)

       with open(output_file, 'w') as f:
           f.write(sdl)

       print(f"✅ Schema exported to {output_file}")

   if __name__ == "__main__":
       if len(sys.argv) != 3:
           print("Usage: python export-schema.py <service_url> <output_file>")
           sys.exit(1)

       export_schema(sys.argv[1], sys.argv[2])
   ```

2. **Add Dependencies**

   ```bash
   # Add to root pyproject.toml or create scripts/requirements.txt
   pip install graphql-core requests
   ```

3. **Test Locally**

   ```bash
   # Start docker-compose
   make demo

   # Export schema from local service
   python scripts/export-schema.py \
     http://localhost:8001 \
     /tmp/journal-schema.graphql

   # Verify SDL format
   cat /tmp/journal-schema.graphql
   ```

**Alternative**: Direct introspection via Hive CLI (simpler but requires service to be running):

```bash
# Hive CLI can introspect directly
hive schema:publish \
  --url "https://service.run.app/graphql" \
  --target "org/project/target"
```

**Deliverables**:
- [ ] `scripts/export-schema.py` created
- [ ] Dependencies documented
- [ ] Tested with local services
- [ ] Usage documented in README

---

### Phase 3: CI/CD Integration - Schema Checks (PR Validation, ~4 hours)

**Goal**: Validate schema changes in pull requests before merging.

**Implementation**:

1. **Create Schema Check Workflow**

   ```yaml
   # .github/workflows/schema-check.yml
   name: GraphQL Schema Check

   on:
     pull_request:
       branches: [staging, main]
       paths:
         - 'src/journal_service/**'
         - 'journal_service/**'
         - 'src/agent_service/**'
         - 'habits_service/**'
         - 'meals_service/**'
         - 'movements_service/**'
         - 'practices_service/**'
         - 'users_service/**'
         - 'src/shared/**'  # Shared code affects all services

   jobs:
     detect-environment:
       runs-on: ubuntu-latest
       outputs:
         environment: ${{ steps.detect.outputs.environment }}
       steps:
         - id: detect
           run: |
             BASE_BRANCH="${{ github.base_ref }}"
             if [[ "$BASE_BRANCH" == "staging" ]]; then
               echo "environment=staging" >> $GITHUB_OUTPUT
             elif [[ "$BASE_BRANCH" == "main" ]]; then
               echo "environment=production" >> $GITHUB_OUTPUT
             else
               echo "environment=staging" >> $GITHUB_OUTPUT
             fi

     check-schemas:
       needs: detect-environment
       runs-on: ubuntu-latest
       strategy:
         fail-fast: false
         matrix:
           service:
             - journal_service
             - agent_service
             - habits_service
             - meals_service
             - movements_service
             - practices_service
             - users_service
       steps:
         - uses: actions/checkout@v4

         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.11'

         - name: Install dependencies
           run: pip install graphql-core requests

         - name: Install Hive CLI
           run: curl -sSL https://graphql-hive.com/install.sh | sh

         - name: Export schema from code
           run: |
             # Start service locally to export schema
             # OR extract from code if services expose schema files
             # For now, we'll skip this and use post-deploy introspection
             echo "Schema validation requires deployed service"

         - name: Check schema compatibility
           env:
             HIVE_TOKEN: ${{ needs.detect-environment.outputs.environment == 'staging' && secrets.HIVE_STAGING_TOKEN || secrets.HIVE_PRODUCTION_TOKEN }}
             ENVIRONMENT: ${{ needs.detect-environment.outputs.environment }}
           run: |
             # This will be populated after Phase 4 when we have schemas to check
             echo "Schema check for ${{ matrix.service }} in ${ENVIRONMENT}"
             # hive schema:check schema.graphql \
             #   --registry.accessToken "$HIVE_TOKEN" \
             #   --target "mindmirror/${ENVIRONMENT}/${{ matrix.service }}" \
             #   --github
   ```

2. **Configure GitHub Integration**

   - Enable Hive GitHub App in repository
   - Grants Hive permission to post Check results on PRs
   - Shows breaking changes inline in PR reviews

**Deliverables**:
- [ ] `.github/workflows/schema-check.yml` created
- [ ] GitHub-Hive integration configured
- [ ] Tested with sample PR
- [ ] Breaking change detection validated

---

### Phase 4: CI/CD Integration - Schema Publishing (Deployment, ~6 hours)

**Goal**: Publish schemas to Hive after successful service deployment.

**Implementation**:

1. **Update Staging Deploy Workflow**

   ```yaml
   # .github/workflows/staging-deploy.yml

   # Add to build-and-push job, after image push
   - name: Publish GraphQL schema to Hive
     if: |
       matrix.service != 'mesh_gateway' &&
       matrix.service != 'celery_worker' &&
       matrix.service != 'web_app' &&
       matrix.service != 'mobile_app'
     env:
       HIVE_TOKEN: ${{ secrets.HIVE_STAGING_TOKEN }}
       SERVICE_NAME: ${{ matrix.service }}
       VERSION_TAG: ${{ needs.detect-changes.outputs.version_tag }}
       GCP_PROJECT_ID: mindmirror-69
       GCP_REGION: us-east4
     run: |
       # Install Hive CLI
       curl -sSL https://graphql-hive.com/install.sh | sh

       # Construct Cloud Run service URL
       SERVICE_URL="https://${SERVICE_NAME}-${VERSION_TAG//./-}-${GCP_REGION}.run.app"

       # Wait for service to be healthy (max 2 minutes)
       echo "⏳ Waiting for ${SERVICE_URL}/health to be ready..."
       for i in {1..24}; do
         if curl -sf "${SERVICE_URL}/health" > /dev/null; then
           echo "✅ Service is healthy"
           break
         fi
         if [ $i -eq 24 ]; then
           echo "❌ Service health check timeout"
           exit 1
         fi
         sleep 5
       done

       # Publish schema via introspection
       echo "📤 Publishing schema to Hive..."
       hive schema:publish \
         --registry.accessToken "$HIVE_TOKEN" \
         --target "mindmirror/staging/${SERVICE_NAME}" \
         --url "${SERVICE_URL}/graphql" \
         --github

       echo "✅ Schema published successfully"
   ```

2. **Update Production Deploy Workflow**

   Same changes as staging, but using:
   - `HIVE_PRODUCTION_TOKEN`
   - `mindmirror-prod` project
   - `mindmirror/production/${SERVICE_NAME}` targets

3. **Handle Schema Publishing Failures**

   ```yaml
   # Add to workflow
   - name: Publish schema (with retry)
     uses: nick-invision/retry@v2
     with:
       timeout_minutes: 5
       max_attempts: 3
       retry_on: error
       command: |
         hive schema:publish \
           --registry.accessToken "$HIVE_TOKEN" \
           --target "mindmirror/staging/${SERVICE_NAME}" \
           --url "${SERVICE_URL}/graphql"
   ```

**Deliverables**:
- [ ] `staging-deploy.yml` updated with schema publishing
- [ ] `production-deploy.yml` updated with schema publishing
- [ ] Schema publishing tested for all 7 services
- [ ] Hive dashboard shows all schemas
- [ ] Supergraph auto-composition verified

---

### Phase 5: Gateway Configuration Update (~3 hours)

**Goal**: Configure gateway to fetch supergraph from Hive CDN instead of local file.

**Implementation**:

1. **Update Gateway Config**

   ```typescript
   // mesh/gateway.config.ts
   import {
     defineConfig,
     extractFromHeader,
     createInlineSigningKeyProvider,
   } from '@graphql-hive/gateway';
   import * as dotenv from 'dotenv';

   dotenv.config();

   export const gatewayConfig = defineConfig({
     host: '0.0.0.0',
     port: 4000,

     /**
      * Supergraph configuration:
      * - PRODUCTION: Fetch from Hive CDN (auto-updates)
      * - LOCAL: Use docker-compose generated file
      */
     supergraph: process.env.HIVE_CDN_ENDPOINT
       ? {
           type: 'hive',
           endpoint: process.env.HIVE_CDN_ENDPOINT,
           key: process.env.HIVE_CDN_KEY,
         }
       : './build/supergraph.graphql',

     /**
      * JWT Authentication and Authorization
      */
     jwt: {
       forward: {
         payload: true,
         token: false,
         extensionsFieldName: 'jwt',
       },
       tokenLookupLocations: [
         extractFromHeader({ name: 'authorization', prefix: 'Bearer' }),
       ],
       signingKeyProviders: [
         createInlineSigningKeyProvider(process.env.SUPABASE_JWT_SECRET as string),
       ],
       tokenVerification: {
         issuer: ['https://gaitofyakycvpwqfoevq.supabase.co/auth/v1'],
         audience: ['authenticated'],
         algorithms: ['HS256'],
       },
       reject: {
         missingToken: true,
         invalidToken: true,
       },
     },

     /** Header propagation configuration */
     propagateHeaders: {
       fromClientToSubgraphs({ request, subgraphName }) {
         const headers: Record<string, string> = {};

         const internalId = request.headers.get('x-internal-id');
         if (internalId) headers['x-internal-id'] = internalId;

         const authorization = request.headers.get('authorization');
         if (authorization) headers['authorization'] = authorization;

         const cookie = request.headers.get('cookie');
         if (cookie) headers['cookie'] = cookie;

         console.log(`🔍 Gateway: Propagating headers to ${subgraphName}:`, headers);
         return headers;
       },
     },

     /** CORS configuration */
     cors: {
       origin: '*',
       methods: ['GET', 'POST', 'OPTIONS'],
       allowedHeaders: ['Content-Type', 'Authorization', 'x-internal-id'],
     },

     /** Logging configuration */
     logging: 'debug',
   });
   ```

2. **Update Gateway Cloud Run Configuration**

   ```hcl
   # infra/modules/gateway/main.tf

   resource "google_cloud_run_service" "gateway" {
     name     = "gateway"
     location = var.region

     template {
       spec {
         containers {
           image = var.gateway_image

           env {
             name  = "HIVE_CDN_ENDPOINT"
             value = var.hive_cdn_endpoint
           }

           env {
             name = "HIVE_CDN_KEY"
             value_from {
               secret_key_ref {
                 name = google_secret_manager_secret.hive_cdn_key.secret_id
                 key  = "latest"
               }
             }
           }

           # ... existing env vars (SUPABASE_JWT_SECRET, etc.)
         }
       }
     }
   }

   resource "google_secret_manager_secret" "hive_cdn_key" {
     secret_id = "hive-cdn-key"
     replication {
       automatic = true
     }
   }
   ```

3. **Add Hive Secrets to Secret Manager**

   ```bash
   # Staging
   echo -n "your-hive-cdn-key" | gcloud secrets create hive-cdn-key \
     --project=mindmirror-69 \
     --data-file=-

   # Production
   echo -n "your-hive-cdn-key" | gcloud secrets create hive-cdn-key \
     --project=mindmirror-prod \
     --data-file=-
   ```

4. **Update tfvars**

   ```hcl
   # infra/staging.auto.tfvars
   gateway_image      = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/mesh:v-xxx"
   hive_cdn_endpoint  = "https://cdn.graphql-hive.com/artifacts/v1/<STAGING_REGISTRY_ID>/<TARGET_ID>/supergraph"

   # infra/production.auto.tfvars
   gateway_image      = "us-east4-docker.pkg.dev/mindmirror-prod/mindmirror/mesh:v-xxx"
   hive_cdn_endpoint  = "https://cdn.graphql-hive.com/artifacts/v1/<PRODUCTION_REGISTRY_ID>/<TARGET_ID>/supergraph"
   ```

**Deliverables**:
- [ ] `mesh/gateway.config.ts` updated with Hive CDN support
- [ ] `infra/modules/gateway/main.tf` updated with Hive env vars
- [ ] Secrets created in GCP Secret Manager
- [ ] tfvars updated with CDN endpoints
- [ ] Gateway tested with CDN-fetched supergraph
- [ ] Fallback to local file verified for development

---

### Phase 6: Intelligent Gateway Redeployment (~4 hours)

**Goal**: Automatically redeploy gateway when supergraph changes.

**Options**:

#### **Option A: Manual Trigger** (Simplest)

After schema publishing, manually trigger gateway redeploy:

```yaml
# .github/workflows/redeploy-gateway.yml
name: Redeploy Gateway

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy (staging or production)'
        required: true
        type: choice
        options:
          - staging
          - production

jobs:
  redeploy:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Cloud Run deployment
        run: |
          gcloud run services update-traffic gateway \
            --to-latest \
            --project=${{ inputs.environment == 'staging' && 'mindmirror-69' || 'mindmirror-prod' }} \
            --region=us-east4
```

#### **Option B: Supergraph Change Detection** (Smarter)

Detect if supergraph actually changed:

```yaml
# Add to staging-deploy.yml after all services publish schemas
- name: Check if supergraph changed
  id: supergraph
  run: |
    # Get current supergraph hash from CDN
    NEW_HASH=$(curl -s -H "X-Hive-CDN-Key: ${{ secrets.HIVE_CDN_KEY }}" \
      ${{ secrets.HIVE_STAGING_CDN_ENDPOINT }} | sha256sum | cut -d' ' -f1)

    # Store in output
    echo "hash=${NEW_HASH}" >> $GITHUB_OUTPUT

    # Compare with previous (stored in Cloud Run env var or GitHub)
    # For now, always redeploy (can optimize later)
    echo "changed=true" >> $GITHUB_OUTPUT

- name: Redeploy gateway if supergraph changed
  if: steps.supergraph.outputs.changed == 'true'
  run: |
    gcloud run services update-traffic gateway \
      --to-latest \
      --project=mindmirror-69 \
      --region=us-east4
```

#### **Option C: Hive Webhook** (Most Elegant)

Configure Hive to trigger GitHub workflow when supergraph changes:

1. **Create Webhook Workflow**

   ```yaml
   # .github/workflows/gateway-webhook.yml
   name: Gateway Update (Hive Webhook)

   on:
     repository_dispatch:
       types: [hive-supergraph-updated]

   jobs:
     redeploy:
       runs-on: ubuntu-latest
       steps:
         - name: Redeploy gateway
           run: |
             ENV=${{ github.event.client_payload.environment }}
             PROJECT=$([[ "$ENV" == "staging" ]] && echo "mindmirror-69" || echo "mindmirror-prod")

             gcloud run services update-traffic gateway \
               --to-latest \
               --project=$PROJECT \
               --region=us-east4
   ```

2. **Configure Hive Webhook**

   In Hive Dashboard:
   - Go to Settings → Webhooks
   - Add webhook: `https://api.github.com/repos/Peleke/MindMirror/dispatches`
   - Add GitHub Personal Access Token
   - Trigger on: Supergraph composition

**Recommendation**: Start with **Option A** (manual), migrate to **Option C** (webhook) later.

**Deliverables**:
- [ ] Gateway redeploy workflow created
- [ ] Tested with schema changes
- [ ] Webhook configured (if using Option C)
- [ ] Deployment documented

---

### Phase 7: Testing & Validation (~4 hours)

**Test Scenarios**:

1. **Schema Change Without Breaking Changes**

   ```bash
   # 1. Add new field to journal_service
   # 2. Deploy to staging
   # 3. Verify schema published to Hive
   # 4. Verify supergraph updated
   # 5. Verify gateway serves new field
   # 6. Query new field from client
   ```

2. **Schema Change With Breaking Changes**

   ```bash
   # 1. Remove field from agent_service
   # 2. Open PR
   # 3. Verify schema:check fails
   # 4. Verify PR blocked
   # 5. Fix breaking change
   # 6. Verify schema:check passes
   ```

3. **Multiple Services Update**

   ```bash
   # 1. Change schemas in journal + habits
   # 2. Deploy both
   # 3. Verify both schemas published
   # 4. Verify supergraph contains both updates
   ```

4. **Gateway Failover**

   ```bash
   # 1. Simulate CDN unavailable
   # 2. Verify gateway falls back gracefully
   # 3. Restore CDN
   # 4. Verify gateway recovers
   ```

**Deliverables**:
- [ ] All test scenarios pass
- [ ] Edge cases documented
- [ ] Rollback procedure documented
- [ ] Performance benchmarks captured

---

### Phase 8: Documentation & Training (~2 hours)

**Documentation Updates**:

1. **Update CLAUDE.md**

   ```markdown
   ## GraphQL Schema Management

   MindMirror uses GraphQL Hive for schema registry and supergraph composition.

   ### Architecture
   - Each GraphQL service publishes its schema to Hive after deployment
   - Hive automatically composes the federated supergraph
   - Gateway fetches supergraph from Hive CDN
   - Local development uses docker-compose mesh-compose service

   ### Schema Changes Workflow
   1. Modify service GraphQL schema
   2. Open PR → Hive validates schema compatibility
   3. Merge PR → Service deploys → Schema publishes to Hive
   4. Hive composes supergraph → Pushes to CDN
   5. Gateway fetches updated supergraph

   ### Hive Dashboard
   - Staging: https://app.graphql-hive.com/mindmirror/staging
   - Production: https://app.graphql-hive.com/mindmirror/production
   ```

2. **Create Troubleshooting Guide**

   ```markdown
   ## Troubleshooting GraphQL Schemas

   ### Schema not updating in gateway
   - Check Hive dashboard for composition errors
   - Verify schema was published successfully
   - Check gateway logs for CDN fetch errors
   - Manually trigger gateway redeploy

   ### Breaking change detection false positive
   - Review breaking change details in Hive
   - Use @deprecated directive for gradual migration
   - Consider creating new field instead of modifying

   ### Schema publish fails
   - Verify service is healthy and accessible
   - Check HIVE_TOKEN is valid
   - Verify target path is correct
   ```

3. **Update README**

   Add Hive setup to local development instructions.

**Deliverables**:
- [ ] CLAUDE.md updated
- [ ] Troubleshooting guide created
- [ ] README updated
- [ ] Team trained on workflow

---

## Migration Path

### Short-term (Keep Current System Working)

1. ✅ Keep `mesh-compose` service for local development
2. ✅ Add Hive schema publishing to workflows (non-breaking addition)
3. ✅ Deploy gateway with conditional supergraph source:
   - Production: Hive CDN
   - Local: docker-compose file

### Medium-term (Hybrid)

1. ✅ Production uses Hive CDN exclusively
2. ✅ Staging uses Hive CDN
3. ✅ Local dev still uses `mesh-compose` (unchanged)

### Long-term (Full Hive)

1. Remove `mesh-compose` from docker-compose
2. Local dev uses `hive dev` command (Hive CLI feature for local development)
3. All environments fetch from Hive registry

---

## Costs & Pricing

### Hive Cloud (Recommended)

**Free Tier** (Sufficient for MindMirror):
- ✅ 1M schema checks/month
- ✅ Unlimited operations
- ✅ 7 targets (we have exactly 7 services)
- ✅ Cloudflare CDN hosting
- ✅ Breaking change detection
- ✅ GitHub integration

**Paid Tiers** (if we outgrow free tier):
- $29/month: 10M checks, 50 targets
- $99/month: 100M checks, unlimited targets

**Self-Hosted** (Alternative):
- Free (open-source)
- Requires PostgreSQL + Redis (already have)
- More DevOps overhead
- No Cloudflare CDN (need own CDN or caching)

---

## Rollback Plan

If Hive integration causes issues:

1. **Immediate Rollback**:
   ```bash
   # Revert gateway to use local supergraph file
   export HIVE_CDN_ENDPOINT=""
   # Gateway will fall back to ./build/supergraph.graphql
   ```

2. **Remove Schema Publishing**:
   - Comment out `hive schema:publish` steps in workflows
   - Services continue deploying normally

3. **Local Development**:
   - Never affected - always uses docker-compose mesh-compose

**No Destructive Changes**: Hive is additive only, can be disabled without breaking anything.

---

## Success Metrics

### Technical Metrics

- ✅ Schema publishing success rate > 99%
- ✅ Supergraph composition time < 30 seconds
- ✅ Gateway supergraph fetch latency < 500ms
- ✅ Zero breaking changes deployed to production
- ✅ Schema check runs on 100% of PRs

### Developer Experience

- ✅ Schema changes visible in Hive within 2 minutes of deployment
- ✅ Breaking change detection catches issues before merge
- ✅ Gateway automatically serves new schemas without manual intervention
- ✅ Clear documentation for schema change workflow

---

## Timeline Estimate

| Phase | Description | Estimated Time |
|-------|-------------|---------------|
| Phase 1 | Hive Cloud Setup | 1 hour |
| Phase 2 | Schema Export Utility | 2 hours |
| Phase 3 | Schema Check Workflow | 4 hours |
| Phase 4 | Schema Publishing | 6 hours |
| Phase 5 | Gateway Configuration | 3 hours |
| Phase 6 | Gateway Redeployment | 4 hours |
| Phase 7 | Testing & Validation | 4 hours |
| Phase 8 | Documentation | 2 hours |
| **Total** | **Full Implementation** | **~26 hours** |

**Phased Approach** (Recommended):
- **Week 1**: Phases 1-2 (Setup + tooling) - 3 hours
- **Week 2**: Phases 3-4 (CI/CD integration) - 10 hours
- **Week 3**: Phases 5-6 (Gateway updates) - 7 hours
- **Week 4**: Phases 7-8 (Testing + docs) - 6 hours

---

## Dependencies & Prerequisites

### Before Starting

- [x] GitOps workflows validated and working
- [x] All services successfully deploying to Cloud Run
- [x] Gateway working with current supergraph approach
- [ ] Hive account created
- [ ] Team familiar with GraphQL Federation concepts

### Technical Requirements

- GraphQL Hive CLI (installed via workflow)
- Python 3.11+ (for schema export utility)
- `graphql-core` Python library
- GitHub repository secrets configured
- GCP Secret Manager access

---

## Related Documentation

- [GraphQL Hive Documentation](https://the-guild.dev/graphql/hive/docs)
- [Hive CLI Reference](https://the-guild.dev/graphql/hive/docs/api-reference/cli)
- [Hive CI/CD Integration](https://the-guild.dev/graphql/hive/docs/other-integrations/ci-cd)
- [GraphQL Federation Spec](https://www.apollographql.com/docs/federation/)

---

## Notes & Considerations

### Why Hive Over Apollo Studio?

- ✅ **Open Source**: Self-hostable if needed
- ✅ **Free Tier**: Better limits for our scale
- ✅ **GraphQL Mesh**: Better integration with our mesh-compose approach
- ✅ **The Guild**: Trusted GraphQL tooling provider

### Alternative: Apollo Router + Federation

Could use Apollo Router instead of Hive Gateway, but:
- Apollo Studio pricing is higher
- Hive has better mesh integration
- Hive is OSS-first (can self-host)

### Schema-First vs Code-First

Current services use **code-first** approach (schema generated from code).

For Hive integration, we can:
- **Option A**: Continue code-first, introspect deployed services
- **Option B**: Switch to schema-first, SDL files in repo
- **Option C**: Hybrid - generate SDL during build

**Recommendation**: Stick with Option A (introspection) for now, minimal changes.

---

## Questions & Open Items

- [ ] Which environment to pilot first? (Staging recommended)
- [ ] Should we add schema:check to pre-commit hooks?
- [ ] Do we want schema versioning/tagging?
- [ ] Should gateway poll CDN or use webhooks?
- [ ] Do we need schema change notifications (Slack/email)?

---

**Status**: Ready for implementation after GitOps validation completes.

**Next Steps**:
1. Complete current GitOps sprint
2. Validate staging + production deployments
3. Review this plan with team
4. Create Hive account
5. Start Phase 1 implementation
