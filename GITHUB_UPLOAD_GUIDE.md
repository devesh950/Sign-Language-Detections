# 🚀 Quick GitHub Upload Guide

## Step-by-Step Instructions to Upload Your Project to GitHub

---

## Method 1: Using GitHub Website (Easiest - No Git Installation Needed)

### Step 1: Create GitHub Account
1. Go to https://github.com/signup
2. Enter your email
3. Create a password
4. Choose a username
5. Verify your account

### Step 2: Create New Repository
1. After logging in, click the **"+"** icon (top right corner)
2. Click **"New repository"**
3. Fill in details:
   - **Repository name:** `sign-language-detection`
   - **Description:** `Real-time sign language detection using AI`
   - **Public** (must be public for free Streamlit deployment)
   - **DON'T** check "Add a README file" (you already have one)
4. Click **"Create repository"**

### Step 3: Upload Files via Website
1. On your new repository page, click **"uploading an existing file"** link
2. **Drag and drop** these files from your folder:
   ```
   streamlit_app.py
   live_sign_detect.py
   perfect_app.py
   sign_model.h5
   labels.pkl
   requirements.txt
   packages.txt
   README.md
   DEPLOYMENT_GUIDE.md
   ACCURACY_GUIDE.txt
   .gitignore
   capture_images.py
   extract_landmarks.py
   train_model.py
   landmarks_dataset.csv
   ```
3. Also drag the **`.streamlit`** folder
4. Add commit message: `Initial commit: Sign language detection app`
5. Click **"Commit changes"**

**Note:** If `sign_model.h5` is too large (>25MB), see Method 2 below.

---

## Method 2: Using Git Command Line (Recommended for Large Files)

### Step 1: Install Git
1. Download Git from: https://git-scm.com/downloads
2. Install with default settings
3. Restart your computer

### Step 2: Configure Git (First Time Only)
Open PowerShell in your project folder and run:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 3: Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `sign-language-detection`
3. Description: `Real-time sign language detection`
4. Make it **Public**
5. Click **"Create repository"**
6. **Copy the repository URL** (looks like: `https://github.com/YOUR_USERNAME/sign-language-detection.git`)

### Step 4: Upload Your Code
Open PowerShell in your project folder and run these commands one by one:

```powershell
# Navigate to your project folder
cd C:\Users\deves\OneDrive\Desktop\sign_language_project_empty

# Initialize Git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Sign language detection app"

# Add GitHub repository (replace YOUR_USERNAME with your actual GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/sign-language-detection.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**When prompted:**
- Enter your GitHub username
- Enter your GitHub password (or Personal Access Token)

---

## Method 3: Using GitHub Desktop (Easiest with GUI)

### Step 1: Install GitHub Desktop
1. Download from: https://desktop.github.com/
2. Install and sign in with your GitHub account

### Step 2: Create Repository
1. Click **"File"** → **"New Repository"**
2. Name: `sign-language-detection`
3. Description: `Real-time sign language detection`
4. Local Path: `C:\Users\deves\OneDrive\Desktop\sign_language_project_empty`
5. Click **"Create Repository"**

### Step 3: Publish to GitHub
1. Click **"Publish repository"** button (top right)
2. **Uncheck** "Keep this code private" (must be public for Streamlit)
3. Click **"Publish Repository"**

Done! Your code is now on GitHub! 🎉

---

## ⚠️ Important Notes

### Large Model File Warning
If `sign_model.h5` is larger than 100MB, you need Git LFS:

```powershell
# Install Git LFS
git lfs install

# Track .h5 files
git lfs track "*.h5"

# Add and commit
git add .gitattributes
git add sign_model.h5
git commit -m "Add model with LFS"
git push
```

### Check Your Model Size
Run this to check file size:
```powershell
Get-Item "C:\Users\deves\OneDrive\Desktop\sign_language_project_empty\sign_model.h5" | Select-Object Name, @{Name="Size MB";Expression={[math]::Round($_.Length/1MB,2)}}
```

---

## ✅ Verify Upload

After uploading, visit:
```
https://github.com/YOUR_USERNAME/sign-language-detection
```

You should see all your files listed!

---

## 🚀 Next Step: Deploy to Streamlit Cloud

Once your code is on GitHub:

1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click **"New app"**
4. Select: `YOUR_USERNAME/sign-language-detection`
5. Main file: `streamlit_app.py`
6. Click **"Deploy!"**

Wait 5-10 minutes and your app will be live! 🎉

---

## 🆘 Troubleshooting

**Problem: "Repository already exists"**
- Choose a different name or delete the old repository

**Problem: "File too large"**
- Use Git LFS (see above)
- Or exclude large files from upload

**Problem: "Authentication failed"**
- Create a Personal Access Token:
  1. GitHub → Settings → Developer settings → Personal access tokens
  2. Generate new token (classic)
  3. Select "repo" scope
  4. Use token as password

**Problem: "Git not found"**
- Install Git from https://git-scm.com/downloads
- Restart PowerShell after installation

---

## 📞 Need Help?

- GitHub Docs: https://docs.github.com/
- Streamlit Docs: https://docs.streamlit.io/
- Git Guide: https://git-scm.com/book/en/v2

---

**Ready to upload? Follow one of the methods above! 🚀**
