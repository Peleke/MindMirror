# Terrateam + Tofu Automation Strategy
**Goal**: Automate the exact manual workflow you have today
**Approach**: GitOps with auto-generated tfvars

---

## Current Manual Workflow (What Works)

```bash
# 1. Build images locally
act -W .github/workflows/local.yaml

# 2. Update defaults.tfvars with new image SHAs
vim infra/defaults.tfvars
# Change: journal_service_container_image = "...:<NEW_SHA>"

# 3. Deploy
cd infra
tofu plan
tofu apply
```

---

## Automated Workflow (What We're Building)

### Staging Deploy (Push to `staging` branch)

```
Developer: git push origin staging
  ↓
GitHub Actions: staging-deploy.yml
  ├─ Detect changed services
  ├─ Build Docker images
  ├─ Tag: v{MAJOR}.{MINOR}.{PATCH}-{GIT_SHA}
  │   Example: v1.2.0-abc1234
  ├─ Push to: us-east4-docker.pkg.dev/mindmirror-staging/mindmirror/<service>:v1.2.0-abc1234
  ├─ Generate staging.auto.tfvars with new image tags
  ├─ Commit staging.auto.tfvars back to staging branch
  ↓
Terrateam (auto-triggered on tfvars commit)
  ├─ Detects: infra/staging.auto.tfvars changed
  ├─ Runs: tofu plan -var-file=staging.auto.tfvars
  ├─ Posts plan to PR (if PR exists) or commit
  ├─ Auto-applies (staging has auto_apply: true)
  ↓
Done ✅
```

### Production Deploy (Push to `main` branch)

```
Developer: git push origin main (or merge PR)
  ↓
GitHub Actions: production-deploy.yml
  ├─ Detect changed services
  ├─ Build Docker images
  ├─ Tag: v{MAJOR}.{MINOR}.{PATCH}-{GIT_SHA}
  ├─ Push to: us-east4-docker.pkg.dev/mindmirror-69/mindmirror/<service>:v1.2.0-abc1234
  ├─ Generate production.auto.tfvars with new image tags
  ├─ Create PR with production.auto.tfvars changes
  ↓
Terrateam (auto-triggered on PR)
  ├─ Detects: infra/production.auto.tfvars changed
  ├─ Runs: tofu plan -var-file=production.auto.tfvars
  ├─ Posts plan as PR comment
  ├─ Waits for approval
  ↓
Human: Reviews plan → comments "terrateam apply"
  ↓
Terrateam: Applies to production
  ↓
Human: Merges PR
  ↓
Done ✅
```

---

## Image Tagging Strategy (Hybrid Semantic Versioning)

Based on: https://reliabilityengineering.substack.com/p/how-to-version-docker-image-correctly

**Format**: `v{MAJOR}.{MINOR}.{PATCH}-{GIT_SHA}`

**Example**: `v1.2.0-abc1234`

**Benefits**:
- ✅ Semantic version for humans
- ✅ Git SHA for traceability
- ✅ Immutable (SHA ensures uniqueness)
- ✅ Sortable (v1.2.0 < v1.3.0)

**Version Bumping**:
- Read from `VERSION` file in repo root
- Bump manually or via conventional commits
- Format: `1.2.0` (no `v` prefix in file)

**Full Tag Examples**:
```
staging: v1.2.0-abc1234
  → us-east4-docker.pkg.dev/mindmirror-staging/mindmirror/agent_service:v1.2.0-abc1234

production: v1.2.0-abc1234
  → us-east4-docker.pkg.dev/mindmirror-69/mindmirror/agent_service:v1.2.0-abc1234
```

**Registry Separation**:
- Staging: Different GCP project (`mindmirror-staging`) OR same project, different repo
- Production: `mindmirror-69` project, `mindmirror` repo
- **Recommendation**: Keep same project, use `mindmirror-staging` repo for simplicity

---

## File Structure

```
infra/
├── main.tf                        # Root module (unchanged)
├── variables.tf                   # Variable definitions (unchanged)
├── defaults.tfvars                # DEPRECATED (replaced by auto.tfvars)
├── staging.auto.tfvars            # Auto-generated for staging ✨
├── production.auto.tfvars         # Auto-generated for production ✨
├── modules/
│   ├── agent_service/
│   ├── journal_service/
│   └── ... (unchanged)
└── .terrateam/
    └── config.yml                 # Terrateam configuration ✨

.github/workflows/
├── staging-deploy.yml             # Build + push staging images ✨
├── production-deploy.yml          # Build + push production images ✨
└── local.yaml                     # Existing local build (keep for manual testing)

scripts/
├── generate-tfvars.sh             # Generate auto.tfvars from image tags ✨
└── bump-version.sh                # Bump VERSION file (optional) ✨

VERSION                             # Current version (e.g., "1.2.0") ✨
```

---

## Terrateam Configuration

**File**: `.terrateam/config.yml`

```yaml
version: 1

automerge: false

# Staging workspace
workspaces:
  - name: staging
    path: infra
    terraform_version: 1.6.0  # Or your Tofu version
    auto_apply: true  # Auto-apply staging changes
    apply_requirements:
      - approved  # Still require approval (comment "terrateam apply")
      # For truly auto-apply, set to [] empty array

    # Use staging.auto.tfvars
    plan_args:
      - -var-file=staging.auto.tfvars

    apply_args:
      - -var-file=staging.auto.tfvars

    # Only trigger on staging branch
    when:
      branch:
        - staging

  # Production workspace
  - name: production
    path: infra
    terraform_version: 1.6.0
    auto_apply: false  # Manual approval required
    apply_requirements:
      - approved

    # Use production.auto.tfvars
    plan_args:
      - -var-file=production.auto.tfvars

    apply_args:
      - -var-file=production.auto.tfvars

    # Only trigger on main branch or PRs to main
    when:
      branch:
        - main
```

**Notes**:
- `auto_apply: true` for staging → immediate deploys
- `auto_apply: false` for production → manual approval via comment
- Separate tfvars files prevent cross-contamination

---

## Auto-Generated tfvars Format

**File**: `infra/staging.auto.tfvars` (example)

```hcl
# Auto-generated by GitHub Actions
# DO NOT EDIT MANUALLY
# Generated at: 2025-10-25T12:34:56Z
# Git SHA: abc1234567890abcdef1234567890abcdef12345

project_id           = "mindmirror-staging"
project_numerical_id = "1234567890"
region               = "us-east4"
gcs_bucket_name      = "traditions-mindmirror-staging"

environment = "staging"
log_level   = "DEBUG"
debug       = "true"

# Image tags (auto-updated)
journal_service_container_image = "us-east4-docker.pkg.dev/mindmirror-staging/mindmirror/journal_service:v1.2.0-abc1234"
agent_service_container_image   = "us-east4-docker.pkg.dev/mindmirror-staging/mindmirror/agent_service:v1.2.0-abc1234"
gateway_container_image         = "us-east4-docker.pkg.dev/mindmirror-staging/mindmirror/mesh:v1.2.0-abc1234"
celery_worker_container_image   = "us-east4-docker.pkg.dev/mindmirror-staging/mindmirror/celery-worker:v1.2.0-abc1234"
habits_service_container_image  = "us-east4-docker.pkg.dev/mindmirror-staging/mindmirror/habits_service:v1.2.0-abc1234"
meals_image                     = "us-east4-docker.pkg.dev/mindmirror-staging/mindmirror/meals_service:v1.2.0-abc1234"
users_image                     = "us-east4-docker.pkg.dev/mindmirror-staging/mindmirror/users_service:v1.2.0-abc1234"
movements_image                 = "us-east4-docker.pkg.dev/mindmirror-staging/mindmirror/movements_service:v1.2.0-abc1234"
practices_image                 = "us-east4-docker.pkg.dev/mindmirror-staging/mindmirror/practices_service:v1.2.0-abc1234"

# Static config (same as defaults.tfvars)
faux_mesh_supabase_id           = "00000000-0000-0000-0000-000000000002"
faux_mesh_user_id               = "00000000-0000-0000-0000-000000000001"

meals_env = {
  OFF_SEARCHALICIOUS_ENABLED = "true"
  OFF_USER_AGENT             = "MindMirrorMeals/1.0 (+support@mindmirror.app)"
}

# Staging-specific overrides
uye_program_template_id              = "be925a11-edfa-4208-9924-d0ecae956aac"
mindmirror_program_template_id       = "1b4fa08a-462b-445e-85a6-6da4d70c6ed"
daily_journaling_program_template_id = "1b4fa08a-462b-445e-85a6-6da4d70c6ed"
```

---

## GitHub Actions Implementation

### Staging Workflow

**File**: `.github/workflows/staging-deploy.yml`

```yaml
name: Deploy to Staging

on:
  push:
    branches:
      - staging

env:
  GCP_PROJECT_ID: mindmirror-staging
  GCP_REGION: us-east4
  ARTIFACT_REGISTRY: us-east4-docker.pkg.dev
  ARTIFACT_REPO: mindmirror

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    outputs:
      version_tag: ${{ steps.version.outputs.tag }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for git describe

      - name: Generate version tag
        id: version
        run: |
          # Read VERSION file
          VERSION=$(cat VERSION | tr -d '\n')

          # Get short SHA
          SHA=$(git rev-parse --short HEAD)

          # Create tag: v1.2.0-abc1234
          TAG="v${VERSION}-${SHA}"
          echo "tag=$TAG" >> $GITHUB_OUTPUT
          echo "Generated tag: $TAG"

      - name: Detect changed services
        id: detect
        run: |
          chmod +x scripts/changed-services.sh
          SERVICES=$(scripts/changed-services.sh origin/main)
          echo "services=$SERVICES" >> $GITHUB_OUTPUT

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_STAGING_SA_KEY }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker
        run: gcloud auth configure-docker ${{ env.ARTIFACT_REGISTRY }} --quiet

      - name: Build and push images
        env:
          VERSION_TAG: ${{ steps.version.outputs.tag }}
        run: |
          SERVICES='${{ steps.detect.outputs.services }}'

          # Build all changed services
          for service in $(echo $SERVICES | jq -r '.[]'); do
            # Map to Dockerfile path
            case "$service" in
              agent_service) DOCKERFILE="src/agent_service/Dockerfile" IMAGE_NAME="agent_service" ;;
              journal_service) DOCKERFILE="src/journal_service/Dockerfile" IMAGE_NAME="journal_service" ;;
              habits_service) DOCKERFILE="habits_service/Dockerfile" IMAGE_NAME="habits_service" ;;
              # ... etc
            esac

            IMAGE="${{ env.ARTIFACT_REGISTRY }}/${{ env.GCP_PROJECT_ID }}/${{ env.ARTIFACT_REPO }}/${IMAGE_NAME}:${VERSION_TAG}"

            echo "Building $IMAGE"
            docker build -t "$IMAGE" -f "$DOCKERFILE" .
            docker push "$IMAGE"
          done

  generate-tfvars:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate staging.auto.tfvars
        env:
          VERSION_TAG: ${{ needs.build-and-push.outputs.version_tag }}
        run: |
          chmod +x scripts/generate-tfvars.sh
          ./scripts/generate-tfvars.sh staging "$VERSION_TAG" > infra/staging.auto.tfvars

      - name: Commit tfvars
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add infra/staging.auto.tfvars
          git commit -m "chore: update staging tfvars to ${{ needs.build-and-push.outputs.version_tag }}"
          git push origin staging
```

### Production Workflow

**File**: `.github/workflows/production-deploy.yml`

Similar to staging, but:
- Pushes to production registry (`mindmirror-69`)
- Creates PR instead of direct commit
- Uses `GCP_PRODUCTION_SA_KEY` secret

---

## Upgrade Path: Cloud Run v1 → v2

**Current**: `google_cloud_run_service` (legacy)

**Target**: `google_cloud_run_v2_service`

**Changes Required**:

```hcl
# Before (v1)
resource "google_cloud_run_service" "agent_service" {
  name     = "agent-service"
  location = var.region

  template {
    spec {
      containers {
        image = var.agent_service_container_image
        env { ... }
      }
    }
  }
}

# After (v2)
resource "google_cloud_run_v2_service" "agent_service" {
  name     = "agent-service"
  location = var.region

  template {
    containers {
      image = var.agent_service_container_image
      env { ... }
    }

    # v2-specific features
    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    # Secret volume mounts
    volumes {
      name = "secrets"
      secret {
        secret       = "database-url"
        items {
          version = "latest"
          path    = "database-url"
        }
      }
    }
  }
}
```

**Migration Strategy**:
1. ✅ Phase 1: Keep v1, get automation working
2. ⏳ Phase 2: Upgrade to v2 after automation is stable (Dec-Jan)
3. ⏳ Phase 3: Add VPC, secret volumes, network security (Jan-Feb)

---

## Network Security (Phase 2)

**Goal**: No public access to backend services, only gateway

```hcl
# Gateway: Public access
resource "google_cloud_run_service_iam_member" "gateway_public" {
  service = google_cloud_run_v2_service.gateway.name
  role    = "roles/run.invoker"
  member  = "allUsers"
}

# Backend services: Private (only gateway can invoke)
resource "google_cloud_run_service_iam_member" "agent_private" {
  service = google_cloud_run_v2_service.agent_service.name
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.gateway.email}"
}

# VPC connector for private communication
resource "google_vpc_access_connector" "connector" {
  name          = "mindmirror-connector"
  region        = var.region
  ip_cidr_range = "10.8.0.0/28"
  network       = "default"
}
```

**Timeline**: Phase 2 (Dec-Jan)

---

## Implementation Checklist

### Week 1: Bootstrap
- [ ] Create `staging` branch
- [ ] Create `VERSION` file (start with `1.0.0`)
- [ ] Install Terrateam GitHub App
- [ ] Configure GCP staging project (or staging Artifact Registry repo)
- [ ] Create staging GCP service account
- [ ] Add `GCP_STAGING_SA_KEY` to GitHub secrets

### Week 2: Automation
- [ ] Create `.terrateam/config.yml`
- [ ] Create `scripts/generate-tfvars.sh`
- [ ] Create `.github/workflows/staging-deploy.yml`
- [ ] Create `.github/workflows/production-deploy.yml`
- [ ] Test staging deploy end-to-end
- [ ] Test production deploy (dry-run)

### Week 3: Production
- [ ] First production deploy via automation
- [ ] Deprecate manual `defaults.tfvars` (keep as backup)
- [ ] Document new workflow for team

### Week 4+: Enhancements
- [ ] Migrate to Cloud Run v2
- [ ] Add VPC networking
- [ ] Implement secret volume mounts
- [ ] Add backend service IAM restrictions

---

## Next Steps

1. **Review this strategy** - Confirm approach
2. **Create staging branch** - `git checkout -b staging && git push origin staging`
3. **I'll generate**:
   - `.terrateam/config.yml`
   - `.github/workflows/staging-deploy.yml`
   - `.github/workflows/production-deploy.yml`
   - `scripts/generate-tfvars.sh`
   - `VERSION` file
   - `infra/staging.auto.tfvars` (initial)
   - `infra/production.auto.tfvars` (initial)

Ready to proceed? 🚀
