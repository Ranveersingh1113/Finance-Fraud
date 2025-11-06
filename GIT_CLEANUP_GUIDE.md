# Git Repository Cleanup Guide

**Issue**: Git repository initialized in wrong location, multiple repos created, large model files

---

## 🚨 **Current Problems**

1. ❌ Git repo initialized in user home directory (wrong location)
2. ❌ Multiple Git repos created (`Finance-Fraud.git/` and main directory)
3. ❌ Large model files need to be excluded
4. ❌ No remote origin configured

---

## ✅ **Step-by-Step Cleanup**

### **Step 1: Navigate to Correct Directory**

```powershell
# Go to your project directory
cd "C:\Users\CL502_05\Downloads\Finance Fraud"

# Verify you're in the right place
ls  # Should see: src/, scripts/, data/, models/, etc.
```

---

### **Step 2: Remove Incorrect Git Repositories**

```powershell
# Remove the Git repo from home directory (if it exists there)
# DON'T run this if you're in the project directory!

# Remove the Finance-Fraud.git directory (bare repo clone)
Remove-Item -Recurse -Force "Finance-Fraud.git" -ErrorAction SilentlyContinue
```

---

### **Step 3: Clean Up Current Repository**

```powershell
# Make sure you're in the project directory
cd "C:\Users\CL502_05\Downloads\Finance Fraud"

# Check if .git exists (should be in project root)
Test-Path .git

# If .git exists but is in wrong location, remove it
# CAUTION: This removes Git history!
# Remove-Item -Recurse -Force .git

# Or keep it if it's in the right place
```

---

### **Step 4: Initialize Clean Repository (If Needed)**

```powershell
# Only if .git doesn't exist or you want to start fresh
cd "C:\Users\CL502_05\Downloads\Finance Fraud"

# Initialize Git (if not already done)
git init

# Check status
git status
```

---

### **Step 5: Verify .gitignore is Correct**

Your `.gitignore` should already have:
```gitignore
*.safetensors
models/fin-e5/
models/deployed/
```

**Verify it exists**:
```powershell
Get-Content .gitignore | Select-String "safetensors"
```

---

### **Step 6: Remove Large Files from Git (If Already Committed)**

```powershell
# Check if files are tracked
git ls-files | Select-String "safetensors"

# If they show up, remove from Git tracking
git rm --cached "models/fin-e5/checkpoints/**/*.safetensors" -r
git rm --cached "models/fin-e5/*.safetensors" -r
git rm --cached "models/deployed/**/*.safetensors" -r

# Remove entire models directory from Git (if accidentally committed)
git rm -r --cached models/ 2>$null

# Commit the removal
git add .gitignore
git commit -m "Exclude model files from Git"
```

---

### **Step 7: Set Up Remote (If Needed)**

```powershell
# Check if remote exists
git remote -v

# If no remote, add it
git remote add origin https://github.com/Ranveersingh1113/Finance-Fraud.git

# Verify
git remote -v
```

---

### **Step 8: First Commit (Clean Start)**

```powershell
# Add all files (respecting .gitignore)
git add .

# Check what will be committed (should NOT include models/)
git status

# Verify models/ is NOT in the list
# If models/ shows up, it means .gitignore isn't working

# Commit
git commit -m "Initial commit - Finance Fraud Detection System"

# Check commit
git log --oneline
```

---

### **Step 9: Push to Remote**

```powershell
# If remote doesn't exist, add it first
git remote add origin https://github.com/Ranveersingh1113/Finance-Fraud.git

# Push (use --force only if you're sure you want to overwrite remote)
git push -u origin master
# OR if remote uses 'main' branch:
git branch -M main
git push -u origin main
```

---

## 🔧 **Quick Fix Commands (Copy-Paste)**

```powershell
# Navigate to project
cd "C:\Users\CL502_05\Downloads\Finance Fraud"

# Remove models from Git tracking (if already committed)
git rm -r --cached models/ 2>$null

# Verify .gitignore has model exclusions
$content = Get-Content .gitignore -Raw
if ($content -notmatch "safetensors") {
    Add-Content .gitignore "`n*.safetensors`nmodels/fin-e5/`nmodels/deployed/"
}

# Add and commit
git add .gitignore
git commit -m "Exclude model files from version control"

# Check status (should NOT show models/)
git status

# If models/ still shows, force remove from index
git rm -r --cached models/
git commit -m "Remove models from Git tracking"
```

---

## ⚠️ **Important Notes**

### **About PowerShell Execution Policy**

The venv activation error is separate:
```powershell
# To fix PowerShell execution policy (run as Administrator):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate venv:
.\financevenv\Scripts\Activate.ps1
```

### **About Model Files**

- ✅ **Keep locally**: Model files stay on your machine
- ✅ **Exclude from Git**: `.gitignore` prevents them from being committed
- ✅ **Don't push**: Large files won't be uploaded to GitHub

---

## 📋 **Verification Checklist**

After cleanup, verify:

```powershell
# 1. Check .gitignore excludes models
git check-ignore models/fin-e5/model.safetensors
# Should output: models/fin-e5/model.safetensors

# 2. Check Git status (should NOT show models/)
git status
# models/ should NOT appear

# 3. Check remote is configured
git remote -v
# Should show: origin https://github.com/...

# 4. Verify branch name
git branch
# Should show: * master or * main
```

---

## 🚨 **If Things Are Really Messed Up**

### **Nuclear Option: Start Fresh**

```powershell
cd "C:\Users\CL502_05\Downloads\Finance Fraud"

# Remove all Git tracking
Remove-Item -Recurse -Force .git

# Reinitialize
git init

# Ensure .gitignore is correct
# (already updated earlier)

# Add files
git add .

# Commit
git commit -m "Initial commit"

# Add remote
git remote add origin https://github.com/Ranveersingh1113/Finance-Fraud.git

# Push
git push -u origin master
```

---

## ✅ **Summary**

**What to do**:
1. Navigate to project directory
2. Remove models from Git tracking (if committed)
3. Verify .gitignore is correct
4. Commit the .gitignore changes
5. Push to remote

**Result**: Clean repository without large model files

---

**Quick Command Sequence**:
```powershell
cd "C:\Users\CL502_05\Downloads\Finance Fraud"
git rm -r --cached models/ 2>$null
git add .gitignore
git commit -m "Exclude model files"
git status  # Verify models/ is gone
```

