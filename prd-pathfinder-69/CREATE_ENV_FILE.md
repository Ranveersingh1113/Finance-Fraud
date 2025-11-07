# 📝 How to Create the .env File

## ⚠️ IMPORTANT: This File is REQUIRED!

Your frontend **will not work** without this file. Follow these steps exactly:

---

## Option 1: PowerShell (Easiest)

Open PowerShell in the `prd-pathfinder-69` folder and run:

```powershell
@"
VITE_API_BASE_URL=http://localhost:8001
VITE_API_KEY=dev-api-key
VITE_API_TIMEOUT=120000
"@ | Out-File -FilePath ".env" -Encoding UTF8
```

---

## Option 2: Command Prompt

Open Command Prompt in the `prd-pathfinder-69` folder and run:

```cmd
(
echo VITE_API_BASE_URL=http://localhost:8001
echo VITE_API_KEY=dev-api-key
echo VITE_API_TIMEOUT=120000
) > .env
```

---

## Option 3: VS Code / Text Editor

1. Open VS Code in the `prd-pathfinder-69` folder
2. Create a new file called `.env` (with the dot at the start!)
3. Paste this content:

```env
VITE_API_BASE_URL=http://localhost:8001
VITE_API_KEY=dev-api-key
VITE_API_TIMEOUT=120000
```

4. Save the file (Ctrl+S)

---

## Option 4: File Explorer

1. Open File Explorer in `prd-pathfinder-69` folder
2. Right-click → New → Text Document
3. Name it `.env` (delete the .txt extension!)
   - **Important:** Make sure "File name extensions" is visible in View menu
4. Open the file and paste:

```
VITE_API_BASE_URL=http://localhost:8001
VITE_API_KEY=dev-api-key
VITE_API_TIMEOUT=120000
```

5. Save and close

---

## ✅ Verify It Worked

### Check the file exists:

**PowerShell:**
```powershell
Get-Content .env
```

**Should output:**
```
VITE_API_BASE_URL=http://localhost:8001
VITE_API_KEY=dev-api-key
VITE_API_TIMEOUT=120000
```

---

## 🐛 Common Issues

### "The system cannot find the file specified"
**Cause:** You're in the wrong folder

**Solution:** 
```powershell
cd "D:\OneDrive\Desktop\Finance Fraud\prd-pathfinder-69"
# Then try again
```

### File shows up as `.env.txt`
**Cause:** Windows is hiding file extensions

**Solution:**
1. Open File Explorer
2. Click View tab
3. Check "File name extensions"
4. Rename `.env.txt` → `.env`

### File is empty or has BOM characters
**Cause:** Wrong encoding

**Solution:** Use the PowerShell command (Option 1) - it handles encoding correctly

---

## 🔐 Configuration Explained

| Variable | Value | Purpose |
|----------|-------|---------|
| `VITE_API_BASE_URL` | `http://localhost:8001` | Backend API address |
| `VITE_API_KEY` | `dev-api-key` | Authentication key (matches backend) |
| `VITE_API_TIMEOUT` | `120000` | Request timeout (2 minutes) |

### Need to change the backend port?

If your backend runs on a different port, change `8001` to your port number.

### Need a different API key?

Match this to whatever you set in your backend's `API_KEY` environment variable.

---

## ✅ After Creating the File

1. **Restart the frontend** if it's already running:
   ```bash
   # Press Ctrl+C in the terminal
   npm run dev
   ```

2. **Check it worked:**
   - Open browser DevTools (F12)
   - Go to Console tab
   - Should NOT see "Cannot connect to backend" errors
   - Network tab should show requests to `http://localhost:8001`

---

## 🎉 That's It!

Once the `.env` file is created, your frontend will automatically connect to the backend.

**Next:** See `BACKEND_CONNECTED.md` for testing instructions.

