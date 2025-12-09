// Popup JavaScript - Token Manager UI
class TokenManagerPopup {
  constructor() {
    console.log('🎨 Initializing Token Manager Popup...');
    this.initializeElements();
    this.loadConfiguration();
    this.setupEventListeners();
    this.updateStatus();
    this.startStatusPolling();
  }

  initializeElements() {
    this.elements = {
      // Configuration inputs
      githubToken: document.getElementById('github-token'),
      repository: document.getElementById('repository'),
      monitoringEnabled: document.getElementById('monitoring-enabled'),
      
      // Buttons
      saveConfig: document.getElementById('save-config'),
      testConnection: document.getElementById('test-connection'),
      forceTokenCheck: document.getElementById('force-token-check'),
      refreshTokenBtn: document.getElementById('refresh-token-btn'),
      copyTokenBtn: document.getElementById('copy-token-btn'),
      viewLogs: document.getElementById('view-logs'),
      clearLogs: document.getElementById('clear-logs'),
      closeLogs: document.getElementById('close-logs'),
      refreshLogs: document.getElementById('refresh-logs'),
      exportLogs: document.getElementById('export-logs'),
      toggleToken: document.getElementById('toggle-token'),
      
      // Status displays
      monitoringStatus: document.getElementById('monitoring-status'),
      lastTokenTime: document.getElementById('last-token-time'),
      tokenExpiry: document.getElementById('token-expiry'),
      githubStatus: document.getElementById('github-status'),
      extensionStatus: document.getElementById('extension-status'),
      
      // Logs
      logs: document.getElementById('logs'),
      logContent: document.getElementById('log-content'),
      logCount: document.getElementById('log-count'),
      
      // Notification container
      notificationContainer: document.getElementById('notification-container')
    };
  }

  async loadConfiguration() {
    try {
      const stored = await chrome.storage.local.get(['config', 'lastToken']);
      
      if (stored.config) {
        this.elements.githubToken.value = stored.config.githubToken || '';
        this.elements.repository.value = stored.config.repository || '';
        this.elements.monitoringEnabled.checked = stored.config.monitoring !== false;
        
        console.log('✅ Configuration loaded');
      }
      
      if (stored.lastToken) {
        console.log('✅ Previous token found');
      }
    } catch (error) {
      console.error('❌ Failed to load configuration:', error);
      this.showNotification('Failed to load configuration', 'error');
    }
  }

  setupEventListeners() {
    // Configuration buttons
    this.elements.saveConfig.addEventListener('click', () => this.saveConfiguration());
    this.elements.testConnection.addEventListener('click', () => this.testGitHubConnection());
    
    // Action buttons
    this.elements.forceTokenCheck.addEventListener('click', () => this.forceTokenCheck());
    this.elements.refreshTokenBtn.addEventListener('click', () => this.refreshToken());
    this.elements.copyTokenBtn.addEventListener('click', () => this.copyToken());
    this.elements.viewLogs.addEventListener('click', () => this.toggleLogs());
    this.elements.clearLogs.addEventListener('click', () => this.clearLogs());
    this.elements.closeLogs.addEventListener('click', () => this.toggleLogs());
    this.elements.refreshLogs.addEventListener('click', () => this.loadLogs());
    this.elements.exportLogs.addEventListener('click', () => this.exportLogs());
    
    // Token visibility toggle
    this.elements.toggleToken.addEventListener('click', () => this.toggleTokenVisibility());
    
    // Enter key to save
    [this.elements.githubToken, this.elements.repository].forEach(input => {
      input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          this.saveConfiguration();
        }
      });
    });
    
    // Monitoring toggle
    this.elements.monitoringEnabled.addEventListener('change', () => {
      this.saveConfiguration();
    });
  }

  async saveConfiguration() {
    const config = {
      githubToken: this.elements.githubToken.value.trim(),
      repository: this.elements.repository.value.trim(),
      monitoring: this.elements.monitoringEnabled.checked
    };

    // Validation
    if (!config.githubToken) {
      this.showNotification('Please enter a GitHub token', 'error');
      this.elements.githubToken.focus();
      return;
    }

    if (!config.repository) {
      this.showNotification('Please enter a repository name', 'error');
      this.elements.repository.focus();
      return;
    }

    if (!config.repository.includes('/')) {
      this.showNotification('Repository format should be: username/repository-name', 'error');
      this.elements.repository.focus();
      return;
    }

    try {
      await chrome.storage.local.set({ config });
      console.log('✅ Configuration saved:', config);
      
      // Notify background script
      chrome.runtime.sendMessage({ action: 'configUpdated', config });
      
      this.showNotification('Configuration saved successfully!', 'success');
      this.updateStatus();
    } catch (error) {
      console.error('❌ Failed to save configuration:', error);
      this.showNotification('Failed to save configuration', 'error');
    }
  }

  async testGitHubConnection() {
    const token = this.elements.githubToken.value.trim();
    const repository = this.elements.repository.value.trim();

    if (!token || !repository) {
      this.showNotification('Please enter GitHub token and repository first', 'error');
      return;
    }

    this.elements.testConnection.disabled = true;
    this.elements.testConnection.innerHTML = '<span class="btn-icon">⏳</span> Testing...';

    try {
      const result = await chrome.runtime.sendMessage({ action: 'testGitHub' });
      
      if (result.success) {
        this.showNotification(`✅ Connected to ${result.repository}`, 'success');
        this.elements.githubStatus.textContent = 'Connected';
        this.elements.githubStatus.className = 'value success';
      } else {
        this.showNotification(`❌ Connection failed: ${result.error}`, 'error');
        this.elements.githubStatus.textContent = 'Failed';
        this.elements.githubStatus.className = 'value error';
      }
    } catch (error) {
      console.error('❌ Test connection failed:', error);
      this.showNotification('Connection test failed', 'error');
    } finally {
      this.elements.testConnection.disabled = false;
      this.elements.testConnection.innerHTML = '<span class="btn-icon">🧪</span> Test Connection';
    }
  }

  forceTokenCheck() {
    console.log('🔍 Forcing token check...');
    
    // Query ALL tabs to find Elia tabs (not just active tab)
    chrome.tabs.query({}, (tabs) => {
      const eliaTabs = tabs.filter(tab => tab.url && (tab.url.includes('elia.one') || tab.url.includes('elia.io')));
      
      if (eliaTabs.length > 0) {
        console.log(`Found ${eliaTabs.length} Elia tab(s)`);
        
        // Send message to all Elia tabs
        eliaTabs.forEach(tab => {
          chrome.tabs.sendMessage(tab.id, { action: 'checkToken' }).catch(err => {
            console.log(`Could not send to tab ${tab.id}:`, err);
          });
        });
        
        chrome.runtime.sendMessage({ action: 'forceTokenCheck' });
        this.showNotification(`Checking ${eliaTabs.length} Elia tab(s) for tokens...`, 'info');
      } else {
        this.showNotification('No Elia tabs found. Please open https://app.elia.io', 'warning');
      }
    });
  }

  refreshToken() {
    console.log('🔄 Refreshing token...');
    this.showNotification('To refresh your token, please logout and login again on the Elia website', 'info');
    
    // Open Elia website in new tab
    chrome.tabs.create({ url: 'https://app.elia.io' });
  }

  async copyToken() {
    console.log('📋 Copying token to clipboard...');
    
    try {
      const stored = await chrome.storage.local.get(['lastToken', 'config']);
      
      if (!stored.lastToken) {
        this.showNotification('No token available. Please check for token first.', 'warning');
        return;
      }
      
      // Copy to clipboard
      await navigator.clipboard.writeText(stored.lastToken);
      
      // Open GitHub secrets page in new tab
      const repository = stored.config?.repository || 'lftremblay/elia-parking-bot';
      const githubUrl = `https://github.com/${repository}/settings/secrets/actions`;
      chrome.tabs.create({ url: githubUrl });
      
      // Show success notification
      this.showNotification('✅ Token copied! GitHub secrets page opened. Paste the token there.', 'success');
      
    } catch (error) {
      console.error('❌ Failed to copy token:', error);
      this.showNotification('Failed to copy token: ' + error.message, 'error');
    }
  }

  toggleLogs() {
    const logsVisible = this.elements.logs.style.display !== 'none';
    this.elements.logs.style.display = logsVisible ? 'none' : 'block';
    
    if (!logsVisible) {
      this.loadLogs();
    }
  }

  async loadLogs() {
    try {
      const response = await chrome.runtime.sendMessage({ action: 'getLogs' });
      const logs = response.logs || [];
      
      this.elements.logCount.textContent = `${logs.length} entries`;
      
      if (logs.length === 0) {
        this.elements.logContent.innerHTML = '<div class="log-placeholder">No logs available</div>';
      } else {
        this.elements.logContent.innerHTML = logs.map(log => `
          <div class="log-entry log-${log.type}">
            <span class="log-timestamp">${log.timestamp}</span>
            <span class="log-type">${this.getLogIcon(log.type)}</span>
            <span class="log-message">${this.escapeHtml(log.message)}</span>
          </div>
        `).join('');
      }
    } catch (error) {
      console.error('❌ Failed to load logs:', error);
      this.elements.logContent.innerHTML = '<div class="log-placeholder error">Failed to load logs</div>';
    }
  }

  async clearLogs() {
    if (confirm('Are you sure you want to clear all logs?')) {
      try {
        await chrome.storage.local.set({ logs: [] });
        this.showNotification('Logs cleared successfully', 'success');
        this.loadLogs();
      } catch (error) {
        console.error('❌ Failed to clear logs:', error);
        this.showNotification('Failed to clear logs', 'error');
      }
    }
  }

  async exportLogs() {
    try {
      const response = await chrome.runtime.sendMessage({ action: 'getLogs' });
      const logs = response.logs || [];
      
      const logText = logs.map(log => 
        `[${log.timestamp}] [${log.type.toUpperCase()}] ${log.message}`
      ).join('\n');
      
      const blob = new Blob([logText], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `elia-token-manager-logs-${new Date().toISOString().split('T')[0]}.txt`;
      a.click();
      URL.revokeObjectURL(url);
      
      this.showNotification('Logs exported successfully', 'success');
    } catch (error) {
      console.error('❌ Failed to export logs:', error);
      this.showNotification('Failed to export logs', 'error');
    }
  }

  toggleTokenVisibility() {
    const input = this.elements.githubToken;
    const button = this.elements.toggleToken;
    
    if (input.type === 'password') {
      input.type = 'text';
      button.textContent = '🙈';
      button.title = 'Hide token';
    } else {
      input.type = 'password';
      button.textContent = '👁️';
      button.title = 'Show token';
    }
  }

  async updateStatus() {
    try {
      const stored = await chrome.storage.local.get(['lastToken', 'config']);
      
      // Update monitoring status
      const monitoring = stored.config?.monitoring !== false;
      this.elements.monitoringStatus.textContent = monitoring ? 'Active' : 'Disabled';
      this.elements.monitoringStatus.className = `value ${monitoring ? 'success' : 'error'}`;

      // Update last token time and expiry
      if (stored.lastToken) {
        const tokenData = this.parseJWT(stored.lastToken);
        if (tokenData && tokenData.iat) {
          const time = new Date(tokenData.iat * 1000).toLocaleString();
          this.elements.lastTokenTime.textContent = time;
          this.elements.lastTokenTime.className = 'value success';
        }
        
        // Update token expiry
        if (tokenData && tokenData.exp) {
          const expiryDate = new Date(tokenData.exp * 1000);
          const now = new Date();
          const daysUntilExpiry = Math.floor((expiryDate - now) / (1000 * 60 * 60 * 24));
          
          this.elements.tokenExpiry.textContent = expiryDate.toLocaleString();
          
          // Color code based on time until expiry
          if (daysUntilExpiry < 1) {
            this.elements.tokenExpiry.className = 'value error';
            this.elements.tokenExpiry.title = 'Token expires today! Please refresh.';
          } else if (daysUntilExpiry < 7) {
            this.elements.tokenExpiry.className = 'value warning';
            this.elements.tokenExpiry.title = `Token expires in ${daysUntilExpiry} days`;
          } else {
            this.elements.tokenExpiry.className = 'value success';
            this.elements.tokenExpiry.title = `Token expires in ${daysUntilExpiry} days`;
          }
        } else {
          this.elements.tokenExpiry.textContent = 'Unknown';
          this.elements.tokenExpiry.className = 'value';
        }
      } else {
        this.elements.lastTokenTime.textContent = 'Never';
        this.elements.lastTokenTime.className = 'value';
        this.elements.tokenExpiry.textContent = 'No token';
        this.elements.tokenExpiry.className = 'value';
      }

      // Update GitHub status
      if (stored.config?.githubToken && stored.config?.repository) {
        this.elements.githubStatus.textContent = 'Configured';
        this.elements.githubStatus.className = 'value success';
      } else {
        this.elements.githubStatus.textContent = 'Not configured';
        this.elements.githubStatus.className = 'value warning';
      }

      // Extension status
      this.elements.extensionStatus.textContent = 'Ready';
      this.elements.extensionStatus.className = 'value success';
      
    } catch (error) {
      console.error('❌ Failed to update status:', error);
    }
  }

  startStatusPolling() {
    // Update status every 5 seconds
    setInterval(() => {
      this.updateStatus();
    }, 5000);
  }

  parseJWT(token) {
    try {
      const [, payload] = token.split('.');
      return JSON.parse(atob(payload));
    } catch (e) {
      return null;
    }
  }

  getLogIcon(type) {
    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️'
    };
    return icons[type] || 'ℹ️';
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <span class="notification-icon">${this.getLogIcon(type)}</span>
      <span class="notification-message">${this.escapeHtml(message)}</span>
    `;
    
    this.elements.notificationContainer.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
      notification.classList.add('show');
    }, 10);
    
    // Remove after 4 seconds
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 4000);
  }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 Token Manager Popup loaded');
  new TokenManagerPopup();
});
