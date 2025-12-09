# 📋 Copy Token Feature - Easy Manual Update!

## ✅ **New Feature Added!**

The extension now has a **"📋 Copy Token"** button that makes it super easy to update GitHub secrets manually!

---

## 🎯 **How It Works**

### **Step 1: Refresh Your Token (When Needed)**
1. Click extension icon
2. Check "Token Expires" field
3. If yellow 🟡 or red 🔴, click **"🔄 Refresh Token"**
4. Logout and login on Elia
5. Extension captures new token automatically ✅

### **Step 2: Copy Token to Clipboard**
1. Click extension icon
2. Click **"📋 Copy Token"** button
3. Token copied to clipboard! ✅
4. Notification shows: "Token copied to clipboard!"

### **Step 3: Update GitHub Secret**
1. Go to: `https://github.com/YOUR-USERNAME/YOUR-REPO/settings/secrets/actions`
2. Find `ELIA_GRAPHQL_TOKEN`
3. Click **"Update"**
4. **Paste** (Ctrl+V) the token
5. Click **"Update secret"** ✅

**Done! Takes 30 seconds total!**

---

## 🔄 **Complete Workflow**

### **Every ~14 Days When Token Expires:**

```
1. Extension shows yellow/red expiry warning
   ↓
2. Click "🔄 Refresh Token" button
   ↓
3. Logout/login on Elia (extension captures new token)
   ↓
4. Click "📋 Copy Token" button
   ↓
5. Go to GitHub secrets page
   ↓
6. Paste and update
   ↓
7. Done! Bot uses new token ✅
```

---

## 📊 **Button Layout**

### **Actions Section:**
```
[🔍 Check for Token Now]  - Scans for token
[🔄 Refresh Token]         - Opens Elia to refresh
[📋 Copy Token]            - Copies to clipboard ← NEW!
[📋 View Logs]             - Shows activity logs
[🗑️ Clear Logs]            - Clears log history
```

---

## ✅ **Benefits**

### **Before (Without Copy Button):**
1. Open DevTools console
2. Run JavaScript command
3. Find token in console output
4. Manually select and copy
5. Go to GitHub
6. Paste and update

**Time**: 2-3 minutes

### **After (With Copy Button):**
1. Click "📋 Copy Token"
2. Go to GitHub
3. Paste and update

**Time**: 30 seconds! 🎉

---

## 🧪 **Testing the Feature**

### **Step 1: Reload Extension**
1. Go to `chrome://extensions/`
2. Find "Elia Token Manager"
3. Click 🔄 reload button

### **Step 2: Test Copy**
1. Click extension icon
2. Click **"📋 Copy Token"**
3. Should see notification: "Token copied to clipboard!"
4. Paste somewhere (Ctrl+V) to verify

### **Step 3: Update GitHub**
1. Go to GitHub secrets page
2. Update `ELIA_GRAPHQL_TOKEN`
3. Paste token
4. Save ✅

---

## 📋 **Notifications**

### **Success:**
```
✅ Token copied to clipboard! Now paste it into GitHub secrets.
```

### **Instructions (2 seconds later):**
```
ℹ️ Go to: GitHub repo → Settings → Secrets → ELIA_GRAPHQL_TOKEN → Update
```

### **No Token:**
```
⚠️ No token available. Please check for token first.
```

---

## 🎯 **Use Cases**

### **1. Regular Token Refresh (Every 2 Weeks)**
- Extension shows expiry warning
- Click Refresh → Logout/Login → Copy → Paste to GitHub

### **2. Initial Setup**
- Extension captures first token
- Click Copy → Paste to GitHub

### **3. After Browser Restart**
- Token still in extension storage
- Click Copy → Paste to GitHub if needed

### **4. Troubleshooting 401 Errors**
- Bot fails with 401
- Check extension expiry
- Refresh if needed
- Copy and update GitHub

---

## ✅ **Summary**

### **What's Automated:**
- ✅ Token detection from Elia
- ✅ Token storage in extension
- ✅ Expiry date monitoring
- ✅ One-click copy to clipboard

### **What's Manual (30 seconds):**
- ⚠️ Paste into GitHub secrets page

### **Frequency:**
- Every ~14 days when token expires
- Takes 30 seconds
- Much better than manual extraction!

---

## 🚀 **Ready to Use!**

**Reload the extension now and you'll see the new "📋 Copy Token" button!**

**Your current token (Dec 23 expiry) is ready to copy! 🎉**
