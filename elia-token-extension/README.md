# 🔌 Elia Token Manager - Chrome Extension

Automated JWT token management for Elia parking bot. This extension monitors your Elia browser session and automatically updates GitHub secrets when new tokens are detected.

---

## 🎯 Features

- ✅ **Automatic Token Detection** - Monitors all Elia API calls for JWT tokens
- ✅ **GitHub Integration** - Automatically updates GitHub secrets
- ✅ **Real-time Monitoring** - Detects tokens instantly on login
- ✅ **Multiple Detection Methods** - localStorage, sessionStorage, cookies, network requests
- ✅ **Activity Logging** - Comprehensive logging for debugging
- ✅ **User-friendly Interface** - Clean popup UI for configuration

---

## 📋 Prerequisites

1. **GitHub Personal Access Token** with `repo` permissions
   - Go to: https://github.com/settings/tokens/new
   - Select scopes: `repo` (full control of private repositories)
   - Generate token and save it securely

2. **Repository Name** - Your parking bot repository (e.g., `username/elia-parking-bot`)

3. **Chrome Browser** - Version 88 or higher

---

## 🚀 Installation

### Step 1: Load Extension in Chrome

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right corner)
3. Click **Load unpacked**
4. Select the `elia-token-extension` folder
5. Extension should appear in your toolbar

### Step 2: Configure Extension

1. Click the **Elia Token Manager** icon in Chrome toolbar
2. Enter your **GitHub Token** (from prerequisites)
3. Enter your **Repository** name (e.g., `tremblof/elia-parking-bot`)
4. Click **Save Configuration**
5. Click **Test Connection** to verify GitHub access

### Step 3: Test Token Detection

1. Open Elia website: https://app.elia.one
2. Log in to your account
3. Extension will automatically detect your JWT token
4. Check extension popup for confirmation
5. Verify GitHub secret was updated

---

## 🔧 Configuration

### GitHub Token Permissions

Your GitHub token needs the following permissions:
- ✅ `repo` - Full control of private repositories
- ✅ `workflow` - Update GitHub Actions workflows (optional)

### Repository Format

Repository must be in format: `username/repository-name`

Examples:
- ✅ `tremblof/elia-parking-bot`
- ✅ `john/parking-automation`
- ❌ `elia-parking-bot` (missing username)
- ❌ `github.com/tremblof/elia-parking-bot` (includes domain)

---

## 📊 How It Works

### Token Detection Flow

```
1. User logs into Elia website
2. Extension monitors network requests
3. JWT token detected in Authorization header
4. Token validated and parsed
5. GitHub secret updated automatically
6. Notification shown to user
7. Bot uses new token on next run
```

### Detection Methods

The extension uses multiple methods to find tokens:

1. **Network Request Monitoring** - Intercepts GraphQL API calls
2. **localStorage Scanning** - Checks browser local storage
3. **sessionStorage Scanning** - Checks session storage
4. **Cookie Monitoring** - Scans browser cookies
5. **DOM Observation** - Watches for token elements
6. **Global Variables** - Checks JavaScript global scope

---

## 🎨 User Interface

### Status Section

- **Monitoring** - Shows if token monitoring is active
- **Last Token** - Timestamp of last detected token
- **GitHub Sync** - GitHub connection status
- **Extension** - Extension health status

### Configuration Section

- **GitHub Token** - Your personal access token
- **Repository** - Target repository for secret updates
- **Monitoring Toggle** - Enable/disable automatic monitoring

### Actions Section

- **Check for Token Now** - Manually trigger token scan
- **View Logs** - Display activity log
- **Clear Logs** - Remove all log entries

---

## 🔍 Troubleshooting

### Token Not Detected

**Problem**: Extension doesn't detect token after login

**Solutions**:
1. Ensure you're on `*.elia.one` domain
2. Check extension is enabled and monitoring is active
3. Try manual token check: Click "Check for Token Now"
4. Open browser console (F12) and check for errors
5. Reload Elia page and login again

### GitHub Update Failed

**Problem**: Token detected but GitHub secret not updated

**Solutions**:
1. Verify GitHub token has `repo` permissions
2. Check repository name format is correct
3. Test GitHub connection in extension popup
4. Ensure repository exists and you have access
5. Check GitHub token hasn't expired

### Extension Not Loading

**Problem**: Extension doesn't appear in Chrome

**Solutions**:
1. Ensure Developer mode is enabled
2. Check for errors in `chrome://extensions/`
3. Reload extension
4. Check manifest.json is valid
5. Verify all files are present

---

## 📝 Activity Logs

### Log Types

- ✅ **Success** - Token detected and updated successfully
- ❌ **Error** - Operation failed (check message for details)
- ⚠️ **Warning** - Non-critical issue occurred
- ℹ️ **Info** - General information message

### Viewing Logs

1. Click extension icon
2. Click "View Logs" button
3. Logs show most recent first
4. Export logs for debugging

### Log Retention

- Logs are stored locally in Chrome storage
- Maximum 100 log entries retained
- Older logs automatically removed
- Clear logs manually if needed

---

## 🔒 Security

### Token Storage

- Tokens stored locally in Chrome's secure storage
- Never transmitted except to GitHub API
- Encrypted at rest by Chrome
- Cleared when extension is removed

### GitHub Token

- Store GitHub token securely
- Use token with minimal required permissions
- Rotate token regularly
- Never share token publicly

### Best Practices

1. Use dedicated GitHub token for this extension
2. Limit token scope to specific repository
3. Monitor GitHub audit log for suspicious activity
4. Revoke token if compromised
5. Keep extension updated

---

## 🚀 Usage with Parking Bot

### Integration Steps

1. **Install Extension** - Follow installation guide above
2. **Configure GitHub** - Set token and repository
3. **Login to Elia** - Extension detects token automatically
4. **Verify Update** - Check GitHub secret was updated
5. **Run Bot** - GitHub Actions uses new token

### Workflow Integration

Your GitHub Actions workflow will automatically use the updated token:

```yaml
- name: Configure environment
  run: |
    echo "ELIA_GRAPHQL_TOKEN=${{ secrets.ELIA_GRAPHQL_TOKEN }}" > .env
```

### Token Refresh Cycle

```
Day 1: Login to Elia → Token detected → GitHub updated
Day 2-30: Bot runs with current token
Day 31: Token expires → Login again → New token detected → GitHub updated
```

---

## 📊 Monitoring & Maintenance

### Daily Checks

- ✅ Extension icon shows no errors
- ✅ GitHub Actions runs successfully
- ✅ Bot books parking spots correctly

### Weekly Checks

- ✅ Review activity logs for issues
- ✅ Verify GitHub token hasn't expired
- ✅ Check extension is up to date

### Monthly Maintenance

- ✅ Rotate GitHub token (security best practice)
- ✅ Clear old logs
- ✅ Verify all features working correctly

---

## 🆘 Support

### Common Issues

1. **Token not updating** - Check GitHub permissions
2. **Extension not monitoring** - Verify monitoring is enabled
3. **GitHub API errors** - Check token and repository name
4. **No token detected** - Ensure you're logged into Elia

### Getting Help

1. Check activity logs for error messages
2. Review troubleshooting section above
3. Verify all prerequisites are met
4. Check browser console for JavaScript errors

---

## 📦 Files Structure

```
elia-token-extension/
├── manifest.json          # Extension configuration
├── background.js          # Token monitoring service
├── content.js             # Page interaction script
├── popup.html             # Extension popup UI
├── popup.js               # Popup functionality
├── styles.css             # UI styling
├── icons/                 # Extension icons
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md             # This file
```

---

## 🎉 Success Indicators

### Extension Working Correctly

- ✅ Status shows "Monitoring: Active"
- ✅ GitHub status shows "Connected"
- ✅ Logs show successful token updates
- ✅ No error notifications

### Bot Integration Working

- ✅ GitHub Actions runs without auth errors
- ✅ Bot successfully books parking spots
- ✅ No manual token updates needed
- ✅ Fully automated operation

---

## 🔄 Updates & Maintenance

### Updating Extension

1. Pull latest code from repository
2. Go to `chrome://extensions/`
3. Click reload icon on extension card
4. Verify version number updated

### Version History

- **v1.0.0** - Initial release with automatic token detection and GitHub integration

---

## 📄 License

This extension is part of the Elia Parking Bot project.

---

## 🎯 Next Steps

1. ✅ Install extension following guide above
2. ✅ Configure GitHub token and repository
3. ✅ Test token detection by logging into Elia
4. ✅ Verify GitHub secret was updated
5. ✅ Run parking bot to confirm integration
6. ✅ Enjoy fully automated token management!

**You now have 100% automated JWT token refresh! 🎉**
