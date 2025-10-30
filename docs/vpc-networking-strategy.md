# VPC Networking Strategy

**Goal**: Private networking for backend services, eliminate public internet traffic between services
**Prerequisites**: Cloud Run v2 migration complete
**Timeline**: 4-6 hours setup per environment

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ PUBLIC INTERNET                                              │
│                                                              │
│  Users/Clients                                              │
└───────────────────┬──────────────────────────────────────────┘
                    │ HTTPS
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ GATEWAY (Public Ingress)                                     │
│ ✅ Accessible from internet                                 │
│ ✅ Authenticates users (JWT)                                │
│ ✅ Routes to backend services                               │
└───────────────────┬──────────────────────────────────────────┘
                    │
                    │ Internal HTTP (VPC)
                    │
       ┌────────────┴────────────┬────────────┬────────────┐
       │                         │            │            │
       ▼                         ▼            ▼            ▼
┌──────────────┐  ┌──────────────┐  ┌─────────────┐  ┌─────────────┐
│ AGENT        │  │ JOURNAL      │  │ HABITS      │  │ MEALS       │
│ SERVICE      │  │ SERVICE      │  │ SERVICE     │  │ SERVICE     │
│              │  │              │  │             │  │             │
│ 🔒 Internal  │  │ 🔒 Internal  │  │ 🔒 Internal │  │ 🔒 Internal │
│    Ingress   │  │    Ingress   │  │    Ingress  │  │    Ingress  │
└──────┬───────┘  └──────┬───────┘  └──────┬──────┘  └──────┬──────┘
       │                 │                 │                │
       │                 │                 │                │
       │        VPC: mindmirror-vpc (10.0.0.0/24)           │
       │                 │                 │                │
       └─────────────────┴─────────────────┴────────────────┘
                         │
                         │ VPC Connector (10.8.0.0/28)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ EXTERNAL SERVICES (via VPC NAT or Direct)                   │
│ - Supabase (PostgreSQL)                                     │
│ - Qdrant Cloud (Vector DB)                                  │
│ - OpenAI API                                                │
│ - Upstash (Redis)                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Network Components

### 1. VPC Network
**Purpose**: Private network for Cloud Run services
**CIDR**: 10.0.0.0/16 (65,536 IPs)

```hcl
resource "google_compute_network" "mindmirror" {
  name                    = "mindmirror-vpc"
  auto_create_subnetworks = false
  project                 = var.project_id
  description             = "VPC for MindMirror Cloud Run services"
}
```

### 2. Cloud Run Subnet
**Purpose**: IP range for Cloud Run VPC connector
**CIDR**: 10.0.0.0/24 (256 IPs)

```hcl
resource "google_compute_subnetwork" "cloudrun" {
  name          = "cloudrun-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.mindmirror.id
  project       = var.project_id

  # Enable Private Google Access (access to GCS, Secret Manager, etc.)
  private_ip_google_access = true

  description = "Subnet for Cloud Run services"
}
```

### 3. VPC Access Connector
**Purpose**: Bridge between Cloud Run (serverless) and VPC
**CIDR**: 10.8.0.0/28 (16 IPs, minimum allowed)

```hcl
resource "google_vpc_access_connector" "connector" {
  name          = "cloudrun-connector"
  region        = var.region
  network       = google_compute_network.mindmirror.name
  ip_cidr_range = "10.8.0.0/28"  # /28 = 16 IPs
  project       = var.project_id

  # Machine type for connector instances
  machine_type = "e2-micro"  # Smallest for staging, e2-standard-4 for production

  # Throughput
  min_throughput = 200  # MB/s
  max_throughput = 1000 # MB/s

  # Instances
  min_instances = 2  # High availability
  max_instances = 10 # Scale under load
}
```

**Cost**: ~$10-15/month base (connector instances run 24/7)

### 4. Cloud NAT (Optional, for static egress IPs)
**Purpose**: Provide static IPs for outbound traffic (useful for IP whitelisting)

```hcl
resource "google_compute_router" "router" {
  name    = "mindmirror-router"
  region  = var.region
  network = google_compute_network.mindmirror.id
  project = var.project_id
}

resource "google_compute_router_nat" "nat" {
  name   = "mindmirror-nat"
  router = google_compute_router.router.name
  region = var.region

  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}
```

**Cost**: ~$30-50/month (NAT gateway + data processing)

### 5. Firewall Rules

```hcl
# Allow internal Cloud Run traffic
resource "google_compute_firewall" "allow_internal_cloudrun" {
  name    = "allow-internal-cloudrun"
  network = google_compute_network.mindmirror.name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["8000", "8001", "8003", "8004", "8005", "8006", "8007", "4000"]
  }

  source_ranges = ["10.0.0.0/24", "10.8.0.0/28"]  # Cloud Run subnet + connector
  description   = "Allow internal traffic between Cloud Run services"
}

# Allow health checks from Google
resource "google_compute_firewall" "allow_health_checks" {
  name    = "allow-health-checks"
  network = google_compute_network.mindmirror.name
  project = var.project_id

  allow {
    protocol = "tcp"
  }

  source_ranges = [
    "130.211.0.0/22",  # Google health check ranges
    "35.191.0.0/16"
  ]

  target_tags = ["cloud-run"]
  description = "Allow Google health checks"
}

# Deny all other ingress
resource "google_compute_firewall" "deny_all" {
  name     = "deny-all-ingress"
  network  = google_compute_network.mindmirror.name
  project  = var.project_id
  priority = 65534  # Low priority (apply last)

  deny {
    protocol = "all"
  }

  source_ranges = ["0.0.0.0/0"]
  description   = "Default deny all ingress"
}
```

---

## Cloud Run v2 Integration

### Gateway (Public Ingress)

```hcl
resource "google_cloud_run_v2_service" "gateway" {
  name     = "gateway"
  location = var.region
  project  = var.project_id

  # Public ingress (entry point from internet)
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    # Connect to VPC
    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"  # Only VPC traffic through VPC
    }

    containers {
      # ... gateway config
    }
  }
}
```

### Backend Services (Internal Ingress)

```hcl
resource "google_cloud_run_v2_service" "agent_service" {
  name     = "agent-service"
  location = var.region
  project  = var.project_id

  # Internal ingress only (no public endpoint)
  ingress = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    # Connect to VPC
    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "ALL_TRAFFIC"  # Route everything through VPC (including external APIs)
      # Or: "PRIVATE_RANGES_ONLY" to only route VPC traffic through VPC
    }

    containers {
      # ... agent config
    }
  }
}
```

---

## Egress Strategy

### Option 1: PRIVATE_RANGES_ONLY (Recommended)
```hcl
vpc_access {
  egress = "PRIVATE_RANGES_ONLY"
}
```

**Behavior**:
- VPC traffic (10.0.0.0/24) → routed through VPC Connector
- Public traffic (Supabase, OpenAI, etc.) → routed directly through internet
- **Pro**: Lower latency for public APIs, lower connector data costs
- **Con**: No static egress IP for public traffic

### Option 2: ALL_TRAFFIC
```hcl
vpc_access {
  egress = "ALL_TRAFFIC"
}
```

**Behavior**:
- ALL traffic → routed through VPC Connector
- Public APIs accessed via Cloud NAT (static IPs possible)
- **Pro**: Static egress IPs (useful for IP whitelisting)
- **Con**: Higher latency, higher connector data costs

**Recommendation**: Use `PRIVATE_RANGES_ONLY` unless you need static IPs for external services

---

## Service Communication Patterns

### Gateway → Backend Service (Internal)
```
Gateway (VPC-connected)
  ↓ Internal HTTP request
  ↓ VPC Connector (10.8.0.0/28)
  ↓ Cloud Run Subnet (10.0.0.0/24)
  ↓ Backend Service (internal ingress)

Result: Private communication, no public internet
```

### Backend Service → External API (e.g., OpenAI)
```
Backend Service (egress: PRIVATE_RANGES_ONLY)
  ↓ Public destination detected
  ↓ Route directly through internet (bypasses VPC)
  ↓ OpenAI API

Result: Lower latency, no VPC data charges
```

### Backend Service → Supabase (External PostgreSQL)
```
Backend Service
  ↓ DATABASE_URL (Supabase endpoint)
  ↓ Routed through internet (Supabase is external)
  ↓ Supabase PostgreSQL

Result: No change from current setup
```

---

## Implementation Steps

### Step 1: Create VPC Resources (Staging)

```bash
cd infra

# Create networking.tf
cat > networking.tf <<'EOF'
resource "google_compute_network" "mindmirror" {
  name                    = "mindmirror-vpc"
  auto_create_subnetworks = false
  project                 = var.project_id
}

resource "google_compute_subnetwork" "cloudrun" {
  name                     = "cloudrun-subnet"
  ip_cidr_range            = "10.0.0.0/24"
  region                   = var.region
  network                  = google_compute_network.mindmirror.id
  private_ip_google_access = true
  project                  = var.project_id
}

resource "google_vpc_access_connector" "connector" {
  name          = "cloudrun-connector"
  region        = var.region
  network       = google_compute_network.mindmirror.name
  ip_cidr_range = "10.8.0.0/28"
  machine_type  = var.environment == "production" ? "e2-standard-4" : "e2-micro"
  min_instances = 2
  max_instances = 10
  project       = var.project_id
}

resource "google_compute_firewall" "allow_internal_cloudrun" {
  name          = "allow-internal-cloudrun"
  network       = google_compute_network.mindmirror.name
  allow {
    protocol = "tcp"
    ports    = ["8000", "8001", "8003", "8004", "8005", "8006", "8007", "4000"]
  }
  source_ranges = ["10.0.0.0/24", "10.8.0.0/28"]
  project       = var.project_id
}
EOF

# Apply to staging
tofu plan -var-file=staging.auto.tfvars
tofu apply -var-file=staging.auto.tfvars

# Wait for VPC Connector to be ready (~5-10 minutes)
gcloud compute networks vpc-access connectors describe cloudrun-connector \
  --region=us-east4 \
  --project=mindmirror-staging
```

### Step 2: Update One Service to Use VPC (Pilot)

**Edit `infra/modules/practices/main.tf`**:
```hcl
resource "google_cloud_run_v2_service" "practices" {
  # ... existing config

  template {
    # Add VPC configuration
    vpc_access {
      connector = var.vpc_connector_id  # Pass from main.tf
      egress    = "PRIVATE_RANGES_ONLY"
    }

    containers {
      # ... existing config
    }
  }
}
```

**Edit `infra/main.tf`**:
```hcl
module "practices_service" {
  source = "./modules/practices"

  # ... existing variables

  # Add VPC connector
  vpc_connector_id = google_vpc_access_connector.connector.id
}
```

**Test**:
```bash
tofu plan -var-file=staging.auto.tfvars
tofu apply -var-file=staging.auto.tfvars

# Verify service still works
curl https://practices-service-staging.run.app/health
```

### Step 3: Migrate All Services to VPC

**Update all service modules** to include `vpc_access` block

**Priority order**:
1. practices (pilot)
2. movements, users (simple services)
3. meals, habits (medium complexity)
4. journal (database-heavy)
5. agent (AI/external APIs)
6. celery_worker
7. gateway (last, critical path)

### Step 4: Enable Internal Ingress for Backend Services

**After all services connected to VPC**:

```hcl
# Backend services: internal only
resource "google_cloud_run_v2_service" "agent_service" {
  ingress = "INGRESS_TRAFFIC_INTERNAL_ONLY"
  # ... rest
}

# Gateway: public
resource "google_cloud_run_v2_service" "gateway" {
  ingress = "INGRESS_TRAFFIC_ALL"
  # ... rest
}
```

**Test**:
```bash
# Backend service should NOT be publicly accessible
curl https://agent-service-staging.run.app/health
# Expected: Error (no public endpoint)

# Gateway should still work
curl https://gateway-staging.run.app/healthcheck
# Expected: 200 OK

# Gateway should be able to reach backend
# (Test via GraphQL queries)
```

---

## Monitoring and Validation

### VPC Connector Health
```bash
gcloud compute networks vpc-access connectors describe cloudrun-connector \
  --region=us-east4 \
  --format=json | jq '.state'

# Expected: "READY"
```

### Service VPC Configuration
```bash
gcloud run services describe agent-service \
  --region=us-east4 \
  --format=json | jq '.spec.template.spec.containers[0].env[] | select(.name=="VPC_CONNECTOR")'
```

### Traffic Flow Verification
```bash
# Check Cloud Run logs for VPC-routed requests
gcloud logging read \
  "resource.type=cloud_run_revision AND jsonPayload.vpcConnector!=null" \
  --limit=10 \
  --format=json
```

---

## Cost Analysis

| Component | Staging | Production | Notes |
|-----------|---------|------------|-------|
| VPC Network | Free | Free | No charge for VPC itself |
| Subnet | Free | Free | No charge for subnets |
| VPC Connector | ~$10/month | ~$30/month | Based on machine type + runtime |
| Firewall Rules | Free | Free | No charge for rules |
| Cloud NAT (optional) | ~$30/month | ~$50/month | If static egress IPs needed |
| Connector Data Transfer | ~$0.01/GB | ~$0.02/GB | Data through connector |
| **Total** | ~$10-40/month | ~$30-80/month | Depends on NAT usage |

**Optimization**:
- Staging: Use `e2-micro` connector, no Cloud NAT
- Production: Use `e2-standard-4` connector, Cloud NAT only if needed

---

## Troubleshooting

### Connector Won't Create
```bash
# Check quota
gcloud compute project-info describe --project=PROJECT_ID

# Check CIDR conflicts
gcloud compute networks subnets list --network=mindmirror-vpc
```

### Services Can't Reach External APIs
```bash
# Verify egress setting
gcloud run services describe SERVICE \
  --format=json | jq '.spec.template.spec.containers[0].env[] | select(.name=="VPC_EGRESS")'

# Should be "PRIVATE_RANGES_ONLY" for external API access

# Check firewall rules
gcloud compute firewall-rules list --filter="network:mindmirror-vpc"
```

### Gateway Can't Reach Backend Services
```bash
# Verify both are VPC-connected
gcloud run services describe gateway --format=json | jq '.spec.template.spec.vpcAccess'
gcloud run services describe agent-service --format=json | jq '.spec.template.spec.vpcAccess'

# Verify internal ingress
gcloud run services describe agent-service --format="value(ingress)"
# Should be: "INGRESS_TRAFFIC_INTERNAL_ONLY"
```

---

## References

- [VPC Serverless Access](https://cloud.google.com/vpc/docs/serverless-vpc-access)
- [Cloud Run Networking](https://cloud.google.com/run/docs/configuring/vpc-direct-vpc)
- [VPC Connector Pricing](https://cloud.google.com/vpc/pricing#serverless-vpc-access)
