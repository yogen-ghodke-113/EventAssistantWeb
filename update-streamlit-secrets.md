# Update Streamlit Cloud Secrets for New Google Gen AI SDK

## Quick Fix for Your Deployed App

Your app is failing because the new Google Gen AI SDK expects a different environment variable name.

### Solution

1. Go to your Streamlit Cloud app dashboard
2. Click **"Settings"** → **"Secrets"**
3. Update your secrets to include the new variable name:

```toml
# Add this NEW secret (required for new SDK)
GOOGLE_API_KEY = "your_actual_api_key_value"

# Keep the old one for backward compatibility (optional)
GEMINI_API_KEY = "your_actual_api_key_value"
```

### What Changed

- **Old SDK**: Expected `GEMINI_API_KEY`
- **New SDK**: Expects `GOOGLE_API_KEY`
- **Our App**: Supports both for compatibility

### After Update

1. Save the secrets
2. Your app should automatically restart
3. The error should be resolved

The app code already supports both variable names, so this is the only change needed!
