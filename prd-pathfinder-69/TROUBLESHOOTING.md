# 🐛 Troubleshooting - Navigation Issues

## Issue: "Only Search is clickable, rest are unclickable"

### Quick Checks:

1. **Can you see all 5 icons at the bottom?**
   - Home (house icon)
   - Cases (folder icon)
   - Search (magnifying glass)
   - Alerts (bell icon)
   - Profile (user icon)

2. **When you click them, what happens?**
   - Do they change color?
   - Does the page change?
   - Do you see any error in console?

### Most Likely Issue: Missing `.env` File

If you haven't created the `.env` file yet, the Dashboard might be stuck loading, which could make the app seem unrespive.

**Fix:**

```bash
# Create .env file in prd-pathfinder-69/
cd prd-pathfinder-69
```

Create a file named `.env` with this content:

```env
VITE_API_BASE_URL=http://localhost:8001
VITE_API_KEY=dev-api-key
VITE_API_TIMEOUT=120000
```

Then **restart the frontend**:

```bash
# Stop frontend (Ctrl+C)
npm run dev
```

### Check Browser Console

Press `F12` to open Developer Tools, then check:

1. **Console Tab** - Any red errors?
2. **Network Tab** - Are API calls failing?

### Test Each Page

Try clicking each bottom nav icon and report what you see:

| Page | Can Click? | Loads? | Error? |
|------|-----------|--------|--------|
| Home (Dashboard) | ? | ? | ? |
| Cases | ? | ? | ? |
| Search | ✅ Yes | ✅ Yes | No |
| Alerts | ? | ? | ? |
| Profile | ? | ? | ? |

### Other Possible Issues

#### Issue 1: Pages Load But Content Doesn't Work

**Symptoms:** Page changes but buttons don't work

**Fix:** This is expected for some features:
- ✅ Search page - Fully working
- ✅ Dashboard - Should show stats (or 0 if no backend)
- 🟡 Cases - "New Case" button not wired yet (normal)
- 🟡 Alerts - Mock data only (normal)
- 🟡 Profile - Mock data only (normal)

#### Issue 2: Z-Index Overlap

**Symptoms:** Can't click anything, pages covered

**Fix:**
```bash
# Check if there's a CSS issue
# In browser console, type:
document.body.style.pointerEvents = "auto"
```

#### Issue 3: Backend Not Running

**Symptoms:** Dashboard stuck loading forever

**Fix:**
```bash
# Start backend in separate terminal
cd "D:/OneDrive/Desktop/Finance Fraud"
.\financevenv\Scripts\activate
python start_api.py
```

### Quick Test Script

Run this in browser console (F12):

```javascript
// Test if navigation works
console.log('Testing navigation...');
document.querySelectorAll('nav a').forEach((link, i) => {
  console.log(`Link ${i}:`, link.href, 'Clickable:', !link.disabled);
});
```

### What to Report

Please tell me:

1. ✅ Can you see all 5 bottom navigation icons?
2. ✅ Can you click them (do they change color)?
3. ✅ Do pages change when you click?
4. ✅ What errors show in console (F12)?
5. ✅ Did you create `.env` file?
6. ✅ Is backend running?

### Emergency Fix

If nothing works, try:

```bash
# Stop frontend
# Clear cache
npm run dev -- --force

# Or rebuild
npm run build
npm run preview
```

