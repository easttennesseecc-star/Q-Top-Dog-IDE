# PowerShell Commands for Kubernetes Cluster RBAC Tiers

## TIER 1: ADMIN (Full Access)

```powershell
# Create Admin Role
kubectl create role admin-role --verb=* --resource=* -n default

# Create Admin RoleBinding
kubectl create rolebinding admin-binding --clusterrole=cluster-admin --serviceaccount=default:admin-user -n default

# Create Admin Service Account
kubectl create serviceaccount admin-user -n default

# Get Admin Token
kubectl -n default describe secret $(kubectl -n default get secret | grep admin-user | awk '{print $1}')
```

---

## TIER 2: DEVELOPER (Read/Write - Deployments, Pods, Services)

```powershell
# Create Developer Role
kubectl create role developer-role `
  --verb=create,update,patch,delete,get,list,watch `
  --resource=deployments,pods,services,configmaps,secrets `
  -n default

# Create Developer RoleBinding
kubectl create rolebinding developer-binding `
  --role=developer-role `
  --serviceaccount=default:developer-user `
  -n default

# Create Developer Service Account
kubectl create serviceaccount developer-user -n default

# Get Developer Token
kubectl -n default describe secret $(kubectl -n default get secret | grep developer-user | awk '{print $1}')
```

---

## TIER 3: VIEWER (Read-Only)

```powershell
# Create Viewer Role
kubectl create role viewer-role `
  --verb=get,list,watch `
  --resource=pods,services,deployments,statefulsets,daemonsets,replicasets `
  -n default

# Create Viewer RoleBinding
kubectl create rolebinding viewer-binding `
  --role=viewer-role `
  --serviceaccount=default:viewer-user `
  -n default

# Create Viewer Service Account
kubectl create serviceaccount viewer-user -n default

# Get Viewer Token
kubectl -n default describe secret $(kubectl -n default get secret | grep viewer-user | awk '{print $1}')
```

---

## TIER 4: DEVELOPER-LIMITED (Create/Update Only - No Delete)

```powershell
# Create Limited Developer Role
kubectl create role dev-limited-role `
  --verb=create,update,patch,get,list,watch `
  --resource=deployments,pods,services,configmaps `
  -n default

# Create Limited Developer RoleBinding
kubectl create rolebinding dev-limited-binding `
  --role=dev-limited-role `
  --serviceaccount=default:dev-limited-user `
  -n default

# Create Limited Developer Service Account
kubectl create serviceaccount dev-limited-user -n default

# Get Limited Developer Token
kubectl -n default describe secret $(kubectl -n default get secret | grep dev-limited-user | awk '{print $1}')
```

---

## TIER 5: OPS (Operations - Full Write Access to Infrastructure)

```powershell
# Create Ops Role
kubectl create role ops-role `
  --verb=create,update,patch,delete,get,list,watch `
  --resource=nodes,persistentvolumes,storageclass,namespaces,clusterrolebindings `
  -n default

# Create Ops RoleBinding
kubectl create rolebinding ops-binding `
  --clusterrole=edit `
  --serviceaccount=default:ops-user `
  -n default

# Create Ops Service Account
kubectl create serviceaccount ops-user -n default

# Get Ops Token
kubectl -n default describe secret $(kubectl -n default get secret | grep ops-user | awk '{print $1}')
```

---

## TIER 6: DEVOPS (Full Cluster Admin)

```powershell
# Create DevOps Service Account
kubectl create serviceaccount devops-user -n default

# Bind to Cluster Admin Role
kubectl create clusterrolebinding devops-binding `
  --clusterrole=cluster-admin `
  --serviceaccount=default:devops-user

# Get DevOps Token
kubectl -n default describe secret $(kubectl -n default get secret | grep devops-user | awk '{print $1}')
```

---

## TIER 7: CI/CD PIPELINE (Deployment Only)

```powershell
# Create CI/CD Role
kubectl create role cicd-role `
  --verb=create,update,patch,get,list `
  --resource=deployments,services,configmaps `
  -n default

# Create CI/CD RoleBinding
kubectl create rolebinding cicd-binding `
  --role=cicd-role `
  --serviceaccount=default:cicd-user `
  -n default

# Create CI/CD Service Account
kubectl create serviceaccount cicd-user -n default

# Get CI/CD Token
kubectl -n default describe secret $(kubectl -n default get secret | grep cicd-user | awk '{print $1}')
```

---

## TIER 8: SUPPORT/DEBUG (Logs & Debugging Only)

```powershell
# Create Support Role
kubectl create role support-role `
  --verb=get,list,watch `
  --resource=pods,services,events,logs `
  -n default

# Create Support RoleBinding
kubectl create rolebinding support-binding `
  --role=support-role `
  --serviceaccount=default:support-user `
  -n default

# Create Support Service Account
kubectl create serviceaccount support-user -n default

# Get Support Token
kubectl -n default describe secret $(kubectl -n default get secret | grep support-user | awk '{print $1}')
```

---

## COMPLETE SETUP SCRIPT (All Tiers at Once)

```powershell
# Create all service accounts
@(
    "admin-user",
    "developer-user", 
    "viewer-user",
    "dev-limited-user",
    "ops-user",
    "devops-user",
    "cicd-user",
    "support-user"
) | ForEach-Object {
    Write-Host "Creating service account: $_" -ForegroundColor Green
    kubectl create serviceaccount $_ -n default
}

# Bind Cluster Admin roles
kubectl create clusterrolebinding devops-binding `
  --clusterrole=cluster-admin `
  --serviceaccount=default:devops-user

kubectl create clusterrolebinding admin-binding `
  --clusterrole=cluster-admin `
  --serviceaccount=default:admin-user

# Create roles
kubectl create role developer-role `
  --verb=create,update,patch,delete,get,list,watch `
  --resource=deployments,pods,services,configmaps,secrets `
  -n default

kubectl create role viewer-role `
  --verb=get,list,watch `
  --resource=pods,services,deployments,statefulsets,daemonsets,replicasets `
  -n default

kubectl create role dev-limited-role `
  --verb=create,update,patch,get,list,watch `
  --resource=deployments,pods,services,configmaps `
  -n default

kubectl create role ops-role `
  --verb=create,update,patch,delete,get,list,watch `
  --resource=nodes,persistentvolumes,storageclass,namespaces `
  -n default

kubectl create role cicd-role `
  --verb=create,update,patch,get,list `
  --resource=deployments,services,configmaps `
  -n default

kubectl create role support-role `
  --verb=get,list,watch `
  --resource=pods,services,events,logs `
  -n default

# Create all bindings
kubectl create rolebinding developer-binding --role=developer-role --serviceaccount=default:developer-user -n default
kubectl create rolebinding viewer-binding --role=viewer-role --serviceaccount=default:viewer-user -n default
kubectl create rolebinding dev-limited-binding --role=dev-limited-role --serviceaccount=default:dev-limited-user -n default
kubectl create rolebinding ops-binding --clusterrole=edit --serviceaccount=default:ops-user -n default
kubectl create rolebinding cicd-binding --role=cicd-role --serviceaccount=default:cicd-user -n default
kubectl create rolebinding support-binding --role=support-role --serviceaccount=default:support-user -n default

Write-Host "All RBAC tiers created successfully!" -ForegroundColor Green
```

---

## GET ALL TOKENS (For Configuration)

```powershell
Write-Host "=== Kubernetes RBAC Tier Tokens ===" -ForegroundColor Cyan
Write-Host "`n"

$users = @(
    "admin-user",
    "developer-user",
    "viewer-user",
    "dev-limited-user",
    "ops-user",
    "devops-user",
    "cicd-user",
    "support-user"
)

foreach ($user in $users) {
    Write-Host "$user Token:" -ForegroundColor Yellow
    $secret = kubectl -n default get secret $(kubectl -n default get secret | Select-String $user | ForEach-Object { $_ -split '\s+' } | Select-Object -First 1) -o jsonpath='{.data.token}'
    [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($secret))
    Write-Host "`n"
}
```

---

## SUMMARY TABLE

```
TIER          | Access Level | Use Case
============================================
1. ADMIN      | Full Access  | Super User
2. DEVOPS     | Cluster Mgmt  | Infrastructure
3. OPS        | Write+Read    | Operations
4. DEVELOPER  | Create/Update | App Development
5. DEV-LIM    | Create Only   | Limited Dev
6. CI/CD      | Deploy Only   | Automation
7. VIEWER     | Read-Only     | Monitoring
8. SUPPORT    | Logs/Debug    | Troubleshooting
```

---

## APPLY TO DIFFERENT NAMESPACES

```powershell
# Create tiers for production namespace
$namespaces = @("production", "staging", "development")

foreach ($ns in $namespaces) {
    kubectl create namespace $ns
    
    kubectl create role dev-role --verb=create,update,patch,delete,get,list,watch --resource=deployments,pods,services -n $ns
    kubectl create rolebinding dev-binding --role=dev-role --serviceaccount=$ns:developer-user -n $ns
    kubectl create serviceaccount developer-user -n $ns
}

Write-Host "Namespaces created with role bindings" -ForegroundColor Green
```
