# 🚀 Quick Installation Guide - Elia Token Manager

Get your automated token refresh working in 10 minutes!

---

## ⚡ Quick Start (5 Steps)

### Step 1: Create GitHub Token (2 minutes)

1. Go to: https://github.com/settings/tokens/new
2. **Note**: `Elia Token Manager`
3. **Expiration**: `No expiration` (or 1 year)
4. **Select scopes**: ✅ `repo` (Full control of private repositories)
5. Click **Generate token**
6. **COPY THE TOKEN** - you won't see it again!

---

### Step 2: Load Extension (1 minute)

1. Open Chrome
2. Navigate to: `chrome://extensions/`
3. Toggle **Developer mode** ON (top-right)
4. Click **Load unpacked**
5. Select folder: `elia-token-extension`
6. Extension appears in toolbar ✅

---

### Step 3: Configure Extension (2 minutes)

1. Click **Elia Token Manager** icon in toolbar
2. Enter **GitHub Token** (from Step 1)
3. Enter **Repository**: `your-username/your-repo-name`
   - Example: `tremblof/elia-parking-bot`
4. Click **Save Configuration**
5. Click **Test Connection** - should show "Connected" ✅

---

### Step 4: Test Token Detection (3 minutes)

1. Open new tab: https://app.elia.one
2. **Log in** to your Elia account
3. Extension automatically detects token
4. Check extension popup - should show:
   - ✅ "Last Token: [timestamp]"
   - ✅ Notification: "Token updated successfully"
5. Check GitHub repository:
   - Go to: Settings → Secrets → Actions
   - Verify `ELIA_GRAPHQL_TOKEN` was updated

---

### Step 5: Verify Bot Integration (2 minutes)

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Find your parking bot workflow
4. Click **Run workflow** (manual trigger)
5. Workflow should run successfully ✅
6. No authentication errors!

---

## 🎉 You're Done!

**Automated token refresh is now active!**

### What Happens Now:

1. **You login to Elia** → Extension detects token
2. **GitHub secret updates** → Automatically
3. **Bot runs daily** → Uses latest token
4. **Zero manual work** → Fully automated!

---

## 🔧 Troubleshooting

### ❌ "GitHub connection failed"

**Fix**: Check your GitHub token:
- Has `repo` permissions?
- Not expired?
- Repository name correct format?

### ❌ "No token detected"

**Fix**: 
1. Ensure you're on `*.elia.one` domain
2. Click "Check for Token Now" in extension
3. Open browser console (F12) for errors
4. Try logging out and back in

### ❌ "Extension not loading"

**Fix**:
1. Ensure Developer mode is ON
2. Check `chrome://extensions/` for errors
3. Click reload icon on extension
4. Verify all files are present

---

## 📊 Quick Reference

### GitHub Token URL
```
https://github.com/settings/tokens/new
```

### Required Permissions
```
✅ repo (Full control of private repositories)
```

### Repository Format
```
username/repository-name
```

### Extension URL
```
chrome://extensions/
```

### Elia Website
```
https://app.elia.one
```

---

## 🎯 Success Checklist

- [ ] GitHub token created with `repo` permissions
- [ ] Extension loaded in Chrome
- [ ] Configuration saved (token + repository)
- [ ] GitHub connection test passed
- [ ] Logged into Elia website
- [ ] Token detected by extension
- [ ] GitHub secret updated
- [ ] Bot workflow runs successfully

**All checked? You're fully automated! 🚀**

---

## 💡 Pro Tips

### Tip 1: Keep Elia Tab Open
- Extension monitors active tabs
- Keep Elia open in background
- Tokens detected automatically on refresh

### Tip 2: Check Logs Regularly
- Click "View Logs" in extension
- Monitor for any errors
- Export logs if troubleshooting

### Tip 3: Test Monthly
- Login to Elia once a month
- Verify token updates
- Check bot still works

### Tip 4: Backup GitHub Token
- Save token in password manager
- Don't lose it - can't retrieve later
- Create new one if lost

---

## 🆘 Need Help?

### Check These First:
1. Extension popup shows "Monitoring: Active"
2. GitHub status shows "Connected"
3. Activity logs show no errors
4. Browser console (F12) has no errors

### Still Having Issues?
1. Review full README.md
2. Check troubleshooting section
3. Verify all prerequisites met
4. Try reinstalling extension

---

## 🎊 Congratulations!

You now have **fully automated JWT token management**!

No more manual token updates. No more expired tokens. No more authentication errors.

**Just set it and forget it! 🎉**
