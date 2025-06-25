# 🚀 Deployment Guide - Investor Event Assistant

## Quick Deploy to Streamlit Cloud (Recommended)

### Prerequisites

1. **GitHub Repository** with your code
2. **Google Gemini API Key** from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Step-by-Step Deployment

#### 1. **Push to GitHub**

```bash
git add .
git commit -m "Deploy Investor Event Assistant"
git push origin main
```

#### 2. **Deploy on Streamlit Cloud**

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository
5. Set:
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: Choose your custom URL

#### 3. **Configure Environment Variables**

In the **Advanced settings** section during deployment:

```toml
[secrets]
GOOGLE_API_KEY = "your_gemini_api_key_here"
```

**Or after deployment:**

1. Go to your app dashboard
2. Click **"Settings"** → **"Secrets"**
3. Add:
   ```
   GOOGLE_API_KEY = "your_actual_api_key_here"
   ```

**Note:** The app also supports the legacy `GEMINI_API_KEY` variable for backward compatibility.

### 📁 **Files Included in Deployment**

- ✅ `app.py` - Main application
- ✅ `Yogen.csv` - Investor database (deploys automatically)
- ✅ `requirements.txt` - Python dependencies
- ✅ `.streamlit/config.toml` - Streamlit configuration (if exists)

### 🔒 **Security Notes**

- ❌ **Never commit your `.env` file** to GitHub
- ✅ **Always use Streamlit Secrets** for API keys in production
- ✅ **The CSV file is safe to commit** (business data, not credentials)

---

## Alternative: Local Development

### Environment Setup

1. Create `.env` file:

   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run locally:
   ```bash
   streamlit run app.py
   ```

---

## Deployment Checklist

- [ ] Repository pushed to GitHub
- [ ] `requirements.txt` includes all dependencies
- [ ] `Yogen.csv` is in the repository
- [ ] Gemini API key obtained
- [ ] Streamlit Cloud account created
- [ ] App deployed with secrets configured
- [ ] App tested and working

---

## Troubleshooting

### Common Issues

**1. "API key not found" error:**

- Check that `GOOGLE_API_KEY` is set in Streamlit Secrets
- Ensure no extra spaces in the key

**2. "CSV file not found" error:**

- Ensure `Yogen.csv` is in the root directory
- Check file name spelling (case-sensitive)

**3. Dependencies not installing:**

- Check `requirements.txt` formatting
- Try redeploying the app

**4. App won't start:**

- Check the logs in Streamlit Cloud dashboard
- Ensure all imports are available

### Support

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Google AI Studio**: [makersuite.google.com](https://makersuite.google.com)

---

## 🎉 Your App is Ready!

Once deployed, your Investor Event Assistant will be available at:
`https://your-app-name.streamlit.app`

Share the link with your team and start exploring investment companies with AI-powered insights!
