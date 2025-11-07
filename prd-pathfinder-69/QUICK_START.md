# Quick Start Guide - Frontend Backend Integration

## ⚡ 5-Minute Setup

### Step 1: Create `.env` File

In `prd-pathfinder-69/` root, create `.env`:

```env
VITE_API_BASE_URL=http://localhost:8001
VITE_API_KEY=dev-api-key
VITE_API_TIMEOUT=120000
```

### Step 2: Start Backend (Terminal 1)

```bash
cd "D:/OneDrive/Desktop/Finance Fraud"
.\financevenv\Scripts\activate
python start_api.py
```

✅ Verify: http://localhost:8001/docs

### Step 3: Start Frontend (Terminal 2)

```bash
cd prd-pathfinder-69
npm run dev
```

✅ Access: http://localhost:8080

### Step 4: Test It!

1. **Dashboard** → Should show stats
2. **Search** → Type "What are SEBI penalties?" → Click search
3. **Should see AI answer + evidence!**

---

## 🎯 What's Working

✅ **Search Page** - Real GraphRAG queries  
✅ **Dashboard** - Real stats from backend  
✅ **Cases** - Loads real cases from database  
✅ **Loading states** - Spinners while fetching  
✅ **Error handling** - Toast notifications  

---

## 🐛 Troubleshooting

**"Cannot connect to backend"**
→ Check backend is running on port 8001

**"403 Forbidden"**
→ Check `.env` has correct API_KEY

**Dashboard shows 0**
→ Normal! No test data yet. Create a case via API:

```bash
curl -X POST http://localhost:8001/cases \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{
    "case_id": "TEST-001",
    "description": "Test case",
    "priority": "high",
    "analyst": "Test User",
    "tags": ["test"]
  }'
```

---

## 📝 Files Created

```
✅ src/lib/api-client.ts          # API client
✅ src/types/api.ts               # TypeScript types
✅ src/services/api.ts            # API functions
✅ src/hooks/useSearch.ts         # Search hook
✅ src/hooks/useCases.ts          # Cases hook
✅ src/hooks/useStats.ts          # Stats hook
✅ src/pages/SearchPage.tsx       # Updated with real API
✅ src/pages/Dashboard.tsx        # Updated with real data
```

---

## 🎓 How to Use

### Search:
```tsx
import { useUnifiedSearch } from '@/hooks/useSearch';

const { mutate: search, data, isPending } = useUnifiedSearch();

search({ query: "your query", n_results: 5 });
```

### Cases:
```tsx
import { useCases } from '@/hooks/useCases';

const { data, isLoading } = useCases('active');
const cases = data?.cases || [];
```

### Stats:
```tsx
import { useSystemStats } from '@/hooks/useStats';

const { data: stats } = useSystemStats();
```

---

**That's it!** Your frontend is now connected to the backend. 🎉

For detailed docs, see `INTEGRATION_SETUP.md`

