# 🏷️ Kubernetes Cluster Tags for Q-IDE

## Cluster-Level Tags

```
environment:production
project:core-ide
owner:devops
cost-center:platform
security:public-facing
```

---

## Node Pool Tags (if using multiple pools)

### Control Plane Nodes
```
environment:production
project:core-ide
owner:devops
cost-center:platform
node-type:control-plane
```

### Worker Nodes - General Purpose
```
environment:production
project:core-ide
owner:devops
cost-center:platform
node-type:worker
workload:general
```

### Worker Nodes - LLM Backend (High Memory)
```
environment:production
project:llm-backend
owner:ml-ops
cost-center:engineering
node-type:worker
workload:llm
performance:high-memory
```

### Worker Nodes - Media Synthesis (GPU)
```
environment:production
project:media-synthesis
owner:backend
cost-center:platform
node-type:worker
workload:media
performance:gpu-required
```

### Worker Nodes - Database
```
environment:production
project:database
owner:devops
cost-center:platform
node-type:worker
workload:database
performance:io-intensive
backup:critical
```

---

## Persistent Volume Tags

### Production Database Storage
```
environment:production
project:database
owner:devops
cost-center:platform
storage-type:database
backup:critical
dr:required
security:pii-handling
security:encryption-required
```

### Cache Storage (Redis)
```
environment:production
project:cache
owner:devops
cost-center:platform
storage-type:cache
backup:weekly
performance:high-memory
```

### Media/Uploads Storage
```
environment:production
project:media-synthesis
owner:backend
cost-center:platform
storage-type:media
backup:weekly
```

---

## Load Balancer Tags

### Main Load Balancer
```
environment:production
project:core-ide
owner:devops
cost-center:platform
security:public-facing
resource-type:load-balancer
```

---

## Namespace Tags (via labels)

### Production Namespace
```
environment:production
project:core-ide
namespace:production
```

### Staging Namespace
```
environment:staging
project:core-ide
namespace:staging
release:beta
```

### Development Namespace
```
environment:development
project:core-ide
namespace:development
security:internal-only
```

---

## Pod/Deployment Labels (for Kubernetes)

### Q-IDE Core
```
app:q-ide
tier:core
environment:production
project:core-ide
```

### LLM Backend
```
app:llm-api
tier:backend
environment:production
project:llm-backend
owner:ml-ops
```

### Database
```
app:database
tier:data
environment:production
project:database
owner:devops
```

### Cache
```
app:redis
tier:data
environment:production
project:cache
```

### Media Synthesis
```
app:media-synthesis
tier:backend
environment:production
project:media-synthesis
```

### Game Engine
```
app:game-engine
tier:backend
environment:production
project:game-engine
```

---

## Summary: Quick Copy Sets

**Cluster-Level:**
```
environment:production, project:core-ide, owner:devops, cost-center:platform, security:public-facing
```

**Worker Nodes - General:**
```
environment:production, project:core-ide, owner:devops, cost-center:platform, node-type:worker, workload:general
```

**Worker Nodes - LLM (High Memory):**
```
environment:production, project:llm-backend, owner:ml-ops, cost-center:engineering, node-type:worker, workload:llm, performance:high-memory
```

**Worker Nodes - GPU (Media):**
```
environment:production, project:media-synthesis, owner:backend, cost-center:platform, node-type:worker, workload:media, performance:gpu-required
```

**Database Storage:**
```
environment:production, project:database, owner:devops, cost-center:platform, storage-type:database, backup:critical, dr:required, security:pii-handling, security:encryption-required
```

**Main Load Balancer:**
```
environment:production, project:core-ide, owner:devops, cost-center:platform, security:public-facing, resource-type:load-balancer
```
