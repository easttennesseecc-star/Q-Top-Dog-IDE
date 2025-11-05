# 🏷️ Digital Ocean Tags Reference for Top Dog

**Purpose**: Organize, manage, and categorize Top Dog resources in Digital Ocean  
**Date**: October 30, 2025  
**Status**: Complete tag taxonomy for deployment

---

## Why Tags Matter

Tags help you:
- ✅ Organize resources by environment, project, cost center
- ✅ Automate billing and cost allocation
- ✅ Implement access controls and permissions
- ✅ Monitor resources and set up alerts
- ✅ Manage infrastructure as code (IaC)
- ✅ Quick filtering and searching across all resources

---

## Recommended Tag Structure

### 1. **Environment Tags** (REQUIRED)
Tags that identify what environment a resource belongs to:

```
environment:production
environment:staging
environment:development
environment:testing
```

**Usage**: Every resource should have ONE environment tag
**Example**: A web server in production gets `environment:production`

### 2. **Project Tags** (REQUIRED)
Tags that identify which Top Dog component:

```
project:core-ide
project:llm-backend
project:game-engine
project:media-synthesis
project:marketplace
project:infrastructure
project:database
project:cache
project:cdn
```

**Usage**: Every resource should have ONE project tag
**Example**: LLM API gets `project:llm-backend`

### 3. **Team/Owner Tags** (RECOMMENDED)
Tags for access control and responsibility:

```
owner:devops
owner:backend
owner:frontend
owner:ml-ops
owner:platform
owner:security
```

**Usage**: Helps identify who maintains resource
**Example**: Database server gets `owner:devops`

### 4. **Cost Center Tags** (RECOMMENDED)
For billing and budget tracking:

```
cost-center:platform
cost-center:engineering
cost-center:operations
cost-center:marketing
```

**Usage**: Helps allocate costs to departments
**Example**: Marketing website gets `cost-center:marketing`

### 5. **Security Tags** (RECOMMENDED)
For compliance and security policies:

```
security:hipaa-ready
security:compliance-required
security:pii-handling
security:public-facing
security:internal-only
security:encryption-required
```

**Usage**: Helps enforce security policies
**Example**: Healthcare database gets `security:hipaa-ready`

### 6. **Performance Tags** (OPTIONAL)
For monitoring and optimization:

```
performance:high-memory
performance:high-cpu
performance:gpu-required
performance:io-intensive
```

**Usage**: Helps identify resource bottlenecks
**Example**: ML training server gets `performance:gpu-required`

### 7. **Backup/DR Tags** (RECOMMENDED)
For disaster recovery:

```
backup:critical
backup:daily
backup:weekly
backup:none
dr:required
dr:optional
```

**Usage**: Helps manage backup policies
**Example**: Production database gets `backup:critical` + `dr:required`

### 8. **Version Tags** (OPTIONAL)
For tracking releases:

```
version:v1.0
version:v1.1
version:v2.0
release:alpha
release:beta
release:stable
```

**Usage**: Helps track which version runs where
**Example**: Staging server gets `version:v2.0` + `release:beta`

---

## Complete Tag Set for Top Dog Deployment

### For Production Web Servers
```
environment:production
project:core-ide
owner:devops
cost-center:platform
security:public-facing
performance:high-cpu
backup:critical
```

### For Production LLM Backend
```
environment:production
project:llm-backend
owner:ml-ops
cost-center:engineering
security:pii-handling
security:encryption-required
performance:high-memory
backup:critical
```

### For Production Database
```
environment:production
project:database
owner:devops
cost-center:platform
security:hipaa-ready
security:compliance-required
security:pii-handling
security:encryption-required
backup:critical
dr:required
```

### For Production Cache (Redis)
```
environment:production
project:cache
owner:devops
cost-center:platform
performance:high-memory
backup:weekly
```

### For Staging Servers
```
environment:staging
project:core-ide
owner:devops
cost-center:platform
security:public-facing
performance:high-cpu
backup:weekly
release:beta
```

### For Development Servers
```
environment:development
project:core-ide
owner:backend
cost-center:engineering
security:internal-only
backup:none
```

### For Game Engine Integration
```
environment:production
project:game-engine
owner:backend
cost-center:platform
performance:high-cpu
performance:gpu-required
backup:weekly
```

### For Media Synthesis (DALL-E, Midjourney)
```
environment:production
project:media-synthesis
owner:backend
cost-center:platform
performance:high-memory
performance:gpu-required
backup:weekly
```

### For AI Marketplace
```
environment:production
project:marketplace
owner:backend
cost-center:platform
security:pii-handling
backup:critical
```

### For CDN / Static Assets
```
environment:production
project:cdn
owner:devops
cost-center:platform
security:public-facing
backup:weekly
```

---

## Tag Naming Conventions

### ✅ DO's
- ✅ Use lowercase letters: `environment:production` (NOT `Environment:Production`)
- ✅ Use hyphens for multi-word tags: `cost-center:platform` (NOT `cost_center:platform`)
- ✅ Keep tags short and descriptive: `owner:devops` (NOT `resource-owner-is-devops-team`)
- ✅ Use consistent prefixes: `environment:`, `project:`, `owner:`, `cost-center:`
- ✅ Use specific values: `environment:production` (NOT `environment:prod-environment`)
- ✅ Keep number of tags reasonable (5-10 per resource)

### ❌ DON'Ts
- ❌ Don't use spaces: `environment: production` → Use `environment:production`
- ❌ Don't use special characters: `owner:devops-team$2025` → Use `owner:devops`
- ❌ Don't use vague tags: `server:important` → Use `backup:critical`
- ❌ Don't mix conventions: Some `environment:prod` and some `env:prod`
- ❌ Don't create unnecessary tags: Avoid `color:blue` or `date:2025`

---

## Sample Digital Ocean Droplet Tags

When creating a Droplet in Digital Ocean, add these tags:

### Production Web Server Droplet
```
Tag 1: environment:production
Tag 2: project:core-ide
Tag 3: owner:devops
Tag 4: cost-center:platform
Tag 5: security:public-facing
```

### Production Database Droplet
```
Tag 1: environment:production
Tag 2: project:database
Tag 3: owner:devops
Tag 4: cost-center:platform
Tag 5: security:hipaa-ready
Tag 6: security:compliance-required
Tag 7: security:pii-handling
Tag 8: backup:critical
Tag 9: dr:required
```

### LLM Backend API Droplet
```
Tag 1: environment:production
Tag 2: project:llm-backend
Tag 3: owner:ml-ops
Tag 4: cost-center:engineering
Tag 5: security:pii-handling
Tag 6: performance:high-memory
Tag 7: backup:critical
```

---

## Using Tags in Digital Ocean

### For Droplets
1. During creation: Add tags in "Select additional options"
2. After creation: Go to Droplet → Tags → Add or Edit
3. Or via CLI: `doctl compute droplet tag create <droplet-id> --tag-names <tag1>,<tag2>`

### For Other Resources (Volumes, Databases, etc.)
1. Each resource type has a Tags section
2. Same naming conventions apply
3. Use consistent tags across all resources

### Querying with Tags
```bash
# List all droplets with production tag
doctl compute droplet list --format Name,ID,MemorySizeMB --tag-name environment:production

# List all resources by project
doctl compute resources list --tag-name project:llm-backend

# List by cost center
doctl compute droplet list --tag-name cost-center:platform
```

---

## Advanced: Tag Automation

### 1. **Billing Reports by Tag**
Digital Ocean can generate cost reports by tag:
- Settings → Billing → Cost Analysis
- Filter by `cost-center` tags
- See breakdown: platform=60%, engineering=40%

### 2. **Monitoring & Alerts by Tag**
- Monitoring → Create Alert
- Set condition for `environment:production`
- Alert only for critical resources

### 3. **Infrastructure as Code with Tags**
In Terraform/Pulumi:
```hcl
resource "digitalocean_droplet" "web" {
  name   = "web-server-01"
  tags = [
    "environment:production",
    "project:core-ide",
    "owner:devops",
    "cost-center:platform",
    "security:public-facing"
  ]
}
```

### 4. **Firewall Rules by Tag**
Apply firewall rules to entire tag groups:
- Firewall → Add Droplets → Select by tag `environment:production`
- All production servers get same security rules automatically

---

## Top Dog Specific Recommendations

### Minimum Required Tags
For simplicity, start with these 3 tags on EVERY resource:

```
1. environment:production  (or staging/development)
2. project:core-ide        (or llm-backend/database/etc)
3. owner:devops            (or ml-ops/backend/etc)
```

### Recommended Additional Tags
Add these for better management:

```
4. cost-center:platform    (for billing)
5. security:public-facing  (or hipaa-ready/pii-handling)
6. backup:critical         (or weekly/daily/none)
```

### For Healthcare/Enterprise Features
**IMPORTANT**: Add these if using HIPAA features:

```
security:hipaa-ready
security:compliance-required
security:pii-handling
security:encryption-required
backup:critical
dr:required
```

---

## Example Complete Deployment

If you're deploying Top Dog with 3 Droplets + 1 Database + 1 CDN:

### Droplet 1: Web Server
```
environment:production
project:core-ide
owner:devops
cost-center:platform
security:public-facing
```

### Droplet 2: LLM Backend
```
environment:production
project:llm-backend
owner:ml-ops
cost-center:engineering
performance:high-memory
backup:weekly
```

### Droplet 3: App Server
```
environment:production
project:core-ide
owner:backend
cost-center:platform
backup:weekly
```

### Database (Managed)
```
environment:production
project:database
owner:devops
cost-center:platform
security:pii-handling
security:encryption-required
backup:critical
dr:required
```

### CDN
```
environment:production
project:cdn
owner:devops
cost-center:platform
security:public-facing
```

---

## Checklist for Digital Ocean Setup

- [ ] Define tag structure (copy from this doc)
- [ ] Create tags in Digital Ocean account settings
- [ ] Tag all existing resources
- [ ] Add tags during new resource creation
- [ ] Set up billing reports by cost-center tags
- [ ] Configure monitoring alerts by environment tag
- [ ] Document tag assignments in team wiki
- [ ] Review tags quarterly (remove unused tags)
- [ ] Enforce tags in IaC templates (Terraform/Pulumi)

---

## Quick Copy-Paste Tag Sets

### Copy these for quick pasting into Digital Ocean:

**Production Web:**
```
environment:production, project:core-ide, owner:devops, cost-center:platform, security:public-facing
```

**Production Database:**
```
environment:production, project:database, owner:devops, cost-center:platform, security:hipaa-ready, security:pii-handling, backup:critical, dr:required
```

**Production LLM API:**
```
environment:production, project:llm-backend, owner:ml-ops, cost-center:engineering, performance:high-memory, backup:critical
```

**Staging Web:**
```
environment:staging, project:core-ide, owner:devops, cost-center:platform, backup:weekly, release:beta
```

**Development Web:**
```
environment:development, project:core-ide, owner:backend, cost-center:engineering, security:internal-only
```

---

## Summary

Top Dog deployment on Digital Ocean should use:

| Tag Type | Examples | Required? |
|----------|----------|-----------|
| Environment | production, staging, development | ✅ YES |
| Project | core-ide, llm-backend, database, cdn | ✅ YES |
| Owner | devops, backend, ml-ops | ✅ YES |
| Cost Center | platform, engineering, operations | ✅ YES |
| Security | hipaa-ready, public-facing, pii-handling | ⚠️ CRITICAL |
| Backup | critical, weekly, daily, none | ✅ YES |
| Performance | high-memory, gpu-required, io-intensive | ⚠️ AS NEEDED |
| Version | v1.0, v2.0, alpha, beta, stable | ⚠️ OPTIONAL |

**Total per resource**: 5-8 tags recommended  
**Start with**: Minimum 3 (environment, project, owner)  
**Add critical**: security tags if handling healthcare data

---

**Ready to deploy on Digital Ocean?** Use the tag sets above for consistent resource organization! 🚀

