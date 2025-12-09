# 🔧 GitHub Secret Update Issue - Manual Workaround

## ❌ **Current Issue**

The extension cannot automatically update GitHub secrets because GitHub requires proper libsodium encryption, which is complex to implement in a browser extension.

**Error**: `Invalid request - encrypted_value does not match pattern`

## ✅ **Temporary Solution: Manual Update**

Until we implement proper encryption, you can manually update the GitHub secret when needed.

### **Option 1: Update via GitHub Website (Easiest)**

1. **Copy your new token from extension**:
   - Click extension icon
   - The token is stored but not displayed
   - Or get it from Elia Network tab (F12 → Network → graphql → Headers → Authorization)

2. **Go to GitHub**:
   - Navigate to: `https://github.com/YOUR-USERNAME/YOUR-REPO/settings/secrets/actions`
   - Find `ELIA_GRAPHQL_TOKEN`
   - Click **"Update"**
   - Paste your new token
   - Click **"Update secret"**

### **Option 2: Update via .env File**

1. **Get token from extension storage**:
   - Open extension
   - Open DevTools (F12)
   - Go to Console
   - Run:
   ```javascript
   chrome.storage.local.get(['lastToken'], (result) => {
     console.log('Token:', result.lastToken);
   });
   ```

2. **Update .env file**:
   ```
   ELIA_GRAPHQL_TOKEN=your-new-token-here
   ```

3. **Test locally**:
   ```bash
   python production_api_bot.py --status
   ```

4. **Update GitHub secret manually** (see Option 1)

---

## 🔄 **When to Update**

### **Check Extension**:
- Token Expires field turns 🟡 yellow (< 7 days)
- Token Expires field turns 🔴 red (< 1 day)

### **Update Process**:
1. Click "🔄 Refresh Token" in extension
2. Logout and login on Elia
3. Extension captures new token automatically
4. **Manually update GitHub secret** (see above)

---

## 🎯 **Future Fix**

To fully automate this, we need to:
1. Add TweetNaCl library to extension
2. Implement proper libsodium encryption
3. Encrypt token before sending to GitHub API

**For now, manual update works perfectly and only needs to be done every 2 weeks!**

---

## ✅ **Current Workaround Status**

### **What Works**:
- ✅ Extension monitors Elia
- ✅ Extension detects new tokens
- ✅ Extension stores tokens locally
- ✅ Extension shows expiry date
- ✅ Refresh button opens Elia

### **What Needs Manual Step**:
- ⚠️ GitHub secret update (manual via website)

### **Frequency**:
- Every ~14 days when token expires
- Takes 30 seconds to update manually

---

## 📋 **Quick Manual Update Steps**

1. **When extension shows yellow/red expiry**:
   - Click "🔄 Refresh Token"
   - Logout/login on Elia
   - Extension captures new token ✅

2. **Update GitHub**:
   - Go to repo settings → Secrets
   - Update `ELIA_GRAPHQL_TOKEN`
   - Paste new token
   - Save ✅

3. **Verify**:
   - Bot continues working
   - Next workflow run uses new token ✅

**That's it! Simple 2-step process every 2 weeks.**

---

## 🎉 **Bottom Line**

The extension still provides huge value:
- ✅ Shows token expiry
- ✅ Captures new tokens automatically
- ✅ One-click refresh process
- ⚠️ Just need to manually paste into GitHub (30 seconds)

**Much better than manually extracting tokens from Network tab every time!**
