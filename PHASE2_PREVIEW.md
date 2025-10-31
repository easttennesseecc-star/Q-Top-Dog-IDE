# 🎨 Phase 2 Preview: React Components (Ready When You Are)

## What's Phase 2?

Build React components that show users their tier status and what they're using.

**Duration**: 2-3 hours
**Complexity**: Medium
**When**: After Phase 1 endpoints are protected (1-2 hours from now)

---

## 📊 Components to Build

### 1. TierInfo Component (30 min)
Shows user's current tier and usage

**Location**: `frontend/src/components/TierInfo.tsx`

**Features**:
- Display current tier name (FREE, PRO, PRO-PLUS, etc.)
- Show tier color badge (green for PRO, gold for PRO-PLUS, etc.)
- Display monthly price
- Show remaining API calls
- Show trial days remaining (if FREE tier)

**Example Display**:
```
┌─────────────────────────────────────┐
│  Your Current Tier: PRO              │
│  Price: $20/month                   │
│  API Calls: 9,500 / 10,000 used     │
│  Next Upgrade: PRO-PLUS ($45/mo)    │
│  └─ Unlock: Custom LLMs             │
└─────────────────────────────────────┘
```

### 2. UsageBar Component (20 min)
Visual progress bar showing API usage

**Location**: `frontend/src/components/UsageBar.tsx`

**Features**:
- Progress bar (0-100%)
- Color changes: green → yellow → red
- Shows "X of Y calls used"
- Warning at 80%
- Blocks at 100%

**Example**:
```
API Usage: ████████░░ 8,000 / 10,000 (80%)
⚠️ Approaching limit - Upgrade to PRO-PLUS
```

### 3. TrialCountdown Component (15 min)
Shows days remaining for FREE tier trial

**Location**: `frontend/src/components/TrialCountdown.tsx`

**Features**:
- Days remaining
- Countdown timer
- "Upgrade Now" CTA when < 2 days

**Example**:
```
🎁 FREE Trial: 3 days left
[UPGRADE NOW FOR $20/mo]
```

### 4. TierUpgradeButton Component (20 min)
Call-to-action for upgrades

**Location**: `frontend/src/components/TierUpgradeButton.tsx`

**Features**:
- Shows "Upgrade to PRO" / "Upgrade to PRO-PLUS" based on current tier
- Links to pricing page
- Shows new features unlocked
- Displays price

**Example**:
```
[UPGRADE TO PRO-PLUS - $45/mo]
Unlock: Custom LLMs, Advanced Analytics
```

### 5. FeatureLockedOverlay Component (20 min)
Shows when feature is locked

**Location**: `frontend/src/components/FeatureLockedOverlay.tsx`

**Features**:
- Overlay on locked features
- Shows required tier
- "Upgrade Now" button
- Shows what tier unlocks it

**Example**:
```
┌─────────────────────────────┐
│ 🔒 This feature requires    │
│    PRO tier ($20/month)     │
│                             │
│ [UPGRADE NOW]               │
└─────────────────────────────┘
```

### 6. PricingComparison Component (45 min)
Shows all 10 tiers side-by-side

**Location**: `frontend/src/components/PricingComparison.tsx`

**Features**:
- 10 tier cards displayed horizontally
- Feature checklist for each tier
- Price highlighted
- Current tier highlighted
- "Upgrade" / "Current" / "Downgrade" buttons

**Example**:
```
┌──────────┬──────────┬──────────┬──────────┐
│ FREE     │ PRO ⭐   │ PRO+     │ TEAM     │
│ $0/mo    │ $20/mo   │ $45/mo   │ $75/mo   │
├──────────┼──────────┼──────────┼──────────┤
│ ✓ Chat   │ ✓ Chat   │ ✓ Chat   │ ✓ Chat   │
│          │ ✓ Code   │ ✓ Code   │ ✓ Code   │
│          │          │ ✓ LLMs   │ ✓ LLMs   │
│          │          │          │ ✓ Team   │
│ TRIAL    │ UPGRADE  │ UPGRADE  │ UPGRADE  │
└──────────┴──────────┴──────────┴──────────┘
```

### 7. UpgradeModal Component (30 min)
Modal that shows upgrade confirmation

**Location**: `frontend/src/components/UpgradeModal.tsx`

**Features**:
- Shows tier details
- Price breakdown
- Features unlocked
- "Confirm Upgrade" button
- Links to payment (Phase 3)

---

## 🎯 Phase 2 Architecture

```
┌─ Frontend ─────────────────────────────┐
│                                        │
│  App.tsx                               │
│    ├─ TierInfo.tsx          (Show tier)│
│    ├─ UsageBar.tsx       (Show usage)  │
│    ├─ TrialCountdown.tsx  (Timer)      │
│    ├─ UpgradeButton.tsx   (CTA)        │
│    ├─ FeatureLocked.tsx   (Overlay)    │
│    ├─ Pricing.tsx          (Page)      │
│    │  └─ PricingComp.tsx  (Table)      │
│    └─ UpgradeModal.tsx    (Modal)      │
│                                        │
├─ Backend API ──────────────────────────┤
│  /api/user/tier       (Get tier info)  │
│  /api/user/usage      (Get usage)      │
│  /api/billing/pricing (Get all tiers)  │
└────────────────────────────────────────┘
```

---

## 📝 API Endpoints Phase 2 Needs

These already exist or will be created:

```
GET /api/user/tier
Response:
{
  "user_id": "user123",
  "tier_name": "pro",
  "tier_level": 1,
  "price": 20,
  "features": ["code_execution", "webhooks"],
  "is_trial": false,
  "trial_expires_at": null,
  "monthly_limit": 10000,
  "daily_used": 120,
  "daily_limit": 333
}

GET /api/billing/pricing
Response:
{
  "tiers": [
    {
      "name": "free",
      "price": 0,
      "features": ["chat"],
      "monthly_limit": 600
    },
    // ... 9 more tiers
  ]
}

GET /api/user/usage
Response:
{
  "today": 120,
  "this_month": 3500,
  "limit_this_month": 10000,
  "remaining": 6500,
  "percentage_used": 35
}
```

---

## 🛠️ Tech Stack for Phase 2

```
Frontend:
├─ React 18+ ✓ (already have)
├─ TypeScript ✓ (already have)
├─ Tailwind CSS ✓ (recommended for styling)
├─ React Query (for API calls)
└─ React Router (for navigation)

State Management:
├─ React Context (for tier data)
├─ zustand (optional, lightweight)
└─ or Redux (if you prefer)

UI Components:
├─ Ant Design or Material-UI (optional)
└─ or CSS-in-JS (Tailwind)
```

---

## 📊 Data Flow Phase 2

```
1. User logs in
   ↓
2. Frontend calls GET /api/user/tier
   ↓
3. Backend returns tier info + usage
   ↓
4. React stores in context/state
   ↓
5. Components display:
   - TierInfo shows "PRO"
   - UsageBar shows "8,000 / 10,000"
   - TrialCountdown hidden (not trial)
   - UpgradeButton shows "PRO-PLUS"
   ↓
6. User clicks "Upgrade"
   ↓
7. Phase 3: Payment flow initiated
```

---

## ⏱️ Phase 2 Timeline

| Component | Time | Complexity |
|-----------|------|-----------|
| TierInfo | 30 min | Easy |
| UsageBar | 20 min | Easy |
| TrialCountdown | 15 min | Easy |
| UpgradeButton | 20 min | Easy |
| FeatureLockedOverlay | 20 min | Medium |
| Pricing Comparison | 45 min | Medium |
| UpgradeModal | 30 min | Medium |
| **Total** | **2.5-3 hrs** | - |

---

## 🎨 Styling Considerations

### Color Scheme by Tier:
```
FREE:        gray (#999999)
PRO:         blue (#0066cc)
PRO-PLUS:    purple (#9933ff)
PRO-TEAM:    teal (#00aa99)
TEAMS:       cyan (#0099ff)
ENTERPRISE:  gold (#ffaa00)
```

### Example Component with Tailwind:
```tsx
const TierBadge = ({ tier }) => {
  const colors = {
    free: 'bg-gray-100 text-gray-800',
    pro: 'bg-blue-100 text-blue-800',
    'pro-plus': 'bg-purple-100 text-purple-800',
    'pro-team': 'bg-teal-100 text-teal-800',
  };
  
  return (
    <div className={`px-4 py-2 rounded-lg font-semibold ${colors[tier]}`}>
      {tier.toUpperCase()}
    </div>
  );
};
```

---

## 🚀 How to Proceed

### Option A: Continue Now (Start Phase 1 + Phase 2 together)
1. ✅ Apply tier pattern to endpoints (1-2 hrs) - Phase 1
2. 🔲 Build React components (2-3 hrs) - Phase 2
3. **Total**: 3-5 hours

### Option B: Finish Phase 1 First
1. ✅ Apply tier pattern to all endpoints
2. ✅ Test everything works
3. 🔲 Then start Phase 2 tomorrow

---

## 📚 Files You'll Create

```
frontend/
├─ src/
│  ├─ components/
│  │  ├─ TierInfo.tsx                ← 30 min
│  │  ├─ UsageBar.tsx               ← 20 min
│  │  ├─ TrialCountdown.tsx         ← 15 min
│  │  ├─ TierUpgradeButton.tsx       ← 20 min
│  │  ├─ FeatureLockedOverlay.tsx    ← 20 min
│  │  ├─ PricingComparison.tsx       ← 45 min
│  │  └─ UpgradeModal.tsx            ← 30 min
│  │
│  ├─ contexts/
│  │  └─ TierContext.tsx              ← 15 min (for state)
│  │
│  ├─ hooks/
│  │  └─ useTierData.ts              ← 10 min (for API calls)
│  │
│  ├─ pages/
│  │  └─ Pricing.tsx                  ← 20 min (wrapper page)
│  │
│  └─ App.tsx                        (update with tier data)
└─ ...
```

---

## 💡 Pro Tips

1. **Start with TierInfo** - It's the simplest and gives you 80% of the value
2. **Use API response as source of truth** - Never hardcode tier data
3. **Add loading states** - Show skeleton while loading tier data
4. **Cache tier data** - Don't refetch on every render
5. **Add error states** - Show message if API fails

---

## 🎯 Phase 2 Success = This Works

```tsx
// User can see:
<TierInfo />                    // Shows: "PRO - $20/mo"
<UsageBar usage={8000} limit={10000} />  // Shows: "8,000 / 10,000"
<TierUpgradeButton />           // Shows: "UPGRADE TO PRO-PLUS"

// And Phase 2 is complete!
```

---

## 🔄 Then Phase 3: Pricing Page

After Phase 2, Phase 3 (Pricing page) is mostly done - you'll already have the components!

---

## Ready to Start Phase 1?

Let me know when you've completed the pattern application and testing. Then we move to Phase 2! 🚀
