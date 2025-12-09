// Background Service Worker - Elia Token Monitor
class EliaTokenMonitor {
  constructor() {
    this.lastToken = null;
    this.config = {
      githubToken: null,
      repository: null,
      monitoring: true,
      lastUpdate: null
    };
    this.logs = [];
    this.initialize();
  }

  async initialize() {
    console.log('🔌 Elia Token Monitor starting...');
    
    // Load configuration
    await this.loadConfiguration();
    
    // Start monitoring network requests
    this.startNetworkMonitoring();
    
    // Setup message listeners
    this.setupMessageListeners();
    
    // Log initialization
    this.addLog('Extension initialized successfully', 'success');
    
    console.log('✅ Elia Token Monitor initialized');
  }

  async loadConfiguration() {
    try {
      const stored = await chrome.storage.local.get(['config', 'lastToken']);
      if (stored.config) {
        this.config = { ...this.config, ...stored.config };
        console.log('📋 Configuration loaded:', this.config);
      }
      if (stored.lastToken) {
        this.lastToken = stored.lastToken;
        console.log('🔑 Previous token loaded');
      }
    } catch (error) {
      console.error('❌ Failed to load configuration:', error);
      this.addLog('Failed to load configuration: ' + error.message, 'error');
    }
  }

  startNetworkMonitoring() {
    console.log('🔍 Starting network request monitoring...');
    
    // Monitor GraphQL API calls for tokens (both .one and .io domains)
    chrome.webRequest.onBeforeSendHeaders.addListener(
      (details) => this.handleGraphQLRequest(details),
      { urls: ["*://api.elia.one/graphql", "*://api.elia.io/graphql"] },
      ["requestHeaders"]
    );

    // Monitor authentication endpoints (both .one and .io domains)
    chrome.webRequest.onBeforeSendHeaders.addListener(
      (details) => this.handleAuthRequest(details),
      { urls: ["*://*.elia.one/auth*", "*://*.elia.one/login*", "*://*.elia.one/signin*",
               "*://*.elia.io/auth*", "*://*.elia.io/login*", "*://*.elia.io/signin*"] },
      ["requestHeaders"]
    );

    // Monitor API responses for new tokens (both .one and .io domains)
    chrome.webRequest.onCompleted.addListener(
      (details) => this.handleAuthResponse(details),
      { urls: ["*://*.elia.one/*", "*://*.elia.io/*"] }
    );
  }

  handleGraphQLRequest(details) {
    if (!this.config.monitoring) {
      console.log('⏸️ Monitoring disabled, skipping GraphQL request');
      return;
    }

    const authHeader = details.requestHeaders.find(
      header => header.name.toLowerCase() === 'authorization'
    );

    if (authHeader && authHeader.value.startsWith('Bearer ')) {
      const token = authHeader.value.substring(7); // Remove 'Bearer '
      
      console.log('🔍 GraphQL request with token detected');
      
      if (this.isNewToken(token)) {
        console.log('🔄 New token detected in GraphQL request');
        this.handleNewToken(token, 'graphql_request');
      }
    }
  }

  handleAuthRequest(details) {
    console.log('🔐 Authentication request detected:', details.url);
    this.addLog('Authentication activity detected', 'info');
    
    // Schedule token check after auth activity
    setTimeout(() => {
      console.log('🔍 Scheduled token check after auth activity');
      this.triggerTokenDetection();
    }, 3000);
  }

  handleAuthResponse(details) {
    // Check if this might be a login response
    if (details.url.includes('auth') || details.url.includes('login') || details.url.includes('signin')) {
      if (details.statusCode >= 200 && details.statusCode < 300) {
        console.log('✅ Successful authentication response');
        this.addLog('Successful authentication response', 'success');
        
        // Schedule token check
        setTimeout(() => {
          this.triggerTokenDetection();
        }, 2000);
      }
    }
  }

  setupMessageListeners() {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      console.log('📨 Message received:', request.action);
      
      switch (request.action) {
        case 'tokenFound':
          this.handleTokenFromPage(request.token, request.source);
          break;
        case 'configUpdated':
          this.updateConfiguration(request.config);
          break;
        case 'forceTokenCheck':
          this.triggerTokenDetection();
          break;
        case 'getLogs':
          sendResponse({ logs: this.logs });
          break;
        case 'testGitHub':
          this.testGitHubConnection().then(sendResponse);
          return true; // Keep message channel open for async response
        default:
          console.log('❓ Unknown message action:', request.action);
      }
    });
  }

  async updateConfiguration(newConfig) {
    try {
      this.config = { ...this.config, ...newConfig };
      await chrome.storage.local.set({ config: this.config });
      console.log('✅ Configuration updated:', this.config);
      this.addLog('Configuration updated successfully', 'success');
    } catch (error) {
      console.error('❌ Failed to update configuration:', error);
      this.addLog('Failed to update configuration: ' + error.message, 'error');
    }
  }

  triggerTokenDetection() {
    // Send message to ALL Elia tabs (not just active tab)
    chrome.tabs.query({}, (tabs) => {
      const eliaTabs = tabs.filter(tab => tab.url && (tab.url.includes('elia.one') || tab.url.includes('elia.io')));
      
      if (eliaTabs.length > 0) {
        console.log(`🎯 Found ${eliaTabs.length} Elia tab(s), triggering token check`);
        
        eliaTabs.forEach(tab => {
          console.log(`📤 Sending token check to tab ${tab.id}: ${tab.url}`);
          chrome.tabs.sendMessage(tab.id, { action: 'checkToken' }).catch(error => {
            console.log(`⚠️ Content script not ready on tab ${tab.id}:`, error);
            this.addLog(`Content script not ready on tab ${tab.id}`, 'warning');
          });
        });
        
        this.addLog(`Checking ${eliaTabs.length} Elia tab(s) for tokens`, 'info');
      } else {
        console.log('⚠️ No Elia tabs found for token detection');
        this.addLog('No Elia tabs found - please open https://app.elia.io', 'warning');
      }
    });
  }

  async handleTokenFromPage(token, source) {
    console.log('📄 Token found from page:', source);
    
    if (this.isNewToken(token)) {
      await this.handleNewToken(token, source);
    }
  }

  isNewToken(newToken) {
    if (!newToken || !this.isValidJWT(newToken)) {
      return false;
    }
    
    if (!this.lastToken) {
      console.log('🆕 First token detected');
      return true;
    }
    
    try {
      // Compare JWT payloads
      const [, oldPayload] = this.lastToken.split('.');
      const [, newPayload] = newToken.split('.');
      
      const oldData = JSON.parse(atob(oldPayload));
      const newData = JSON.parse(atob(newPayload));
      
      // Check if it's a different token (different jti, iat, or exp)
      const isDifferent = oldData.jti !== newData.jti || 
                         oldData.iat !== newData.iat || 
                         oldData.exp !== newData.exp;
      
      if (isDifferent) {
        console.log('🔄 Token difference detected:', {
          oldJti: oldData.jti,
          newJti: newData.jti,
          oldIat: oldData.iat,
          newIat: newData.iat
        });
      }
      
      return isDifferent;
    } catch (e) {
      console.error('❌ Error comparing tokens:', e);
      // If parsing fails, assume it's new
      return true;
    }
  }

  isValidJWT(token) {
    if (typeof token !== 'string') return false;
    
    const parts = token.split('.');
    if (parts.length !== 3) return false;
    
    try {
      // Try to decode payload
      const payload = JSON.parse(atob(parts[1]));
      return payload && payload.exp && payload.iat;
    } catch (e) {
      return false;
    }
  }

  async handleNewToken(token, source) {
    console.log('🎯 Processing new token from:', source);
    this.addLog(`New token detected from ${source}`, 'info');
    
    try {
      // Validate token
      const tokenData = this.parseJWT(token);
      if (!tokenData) {
        console.error('❌ Invalid token format');
        this.addLog('Invalid token format received', 'error');
        return;
      }

      console.log('📋 Token data:', {
        exp: new Date(tokenData.exp * 1000).toLocaleString(),
        iat: new Date(tokenData.iat * 1000).toLocaleString(),
        sub: tokenData.sub
      });

      // Store token locally
      this.lastToken = token;
      await chrome.storage.local.set({ lastToken: token });
      this.config.lastUpdate = new Date().toISOString();
      await chrome.storage.local.set({ config: this.config });

      // Update GitHub secret
      const success = await this.updateGitHubSecret(token);
      
      if (success) {
        console.log('✅ Token successfully updated in GitHub');
        this.addLog('Token successfully updated in GitHub', 'success');
        this.showNotification('Elia token updated successfully!', 'success');
      } else {
        console.error('❌ Failed to update GitHub token');
        this.addLog('Failed to update GitHub token - check configuration', 'error');
        this.showNotification('Failed to update token - check configuration', 'error');
      }

    } catch (error) {
      console.error('❌ Error handling new token:', error);
      this.addLog('Error handling new token: ' + error.message, 'error');
      this.showNotification('Token update failed: ' + error.message, 'error');
    }
  }

  parseJWT(token) {
    try {
      const [, payload] = token.split('.');
      return JSON.parse(atob(payload));
    } catch (e) {
      console.error('❌ Failed to parse JWT:', e);
      return null;
    }
  }

  async updateGitHubSecret(token) {
    if (!this.config.githubToken || !this.config.repository) {
      console.error('❌ GitHub configuration missing');
      this.addLog('GitHub configuration missing - please set token and repository', 'error');
      return false;
    }

    console.log('🔄 Updating GitHub secret...');
    
    try {
      // Encode the token for GitHub API
      const encodedToken = btoa(token)
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');

      const response = await fetch(`https://api.github.com/repos/${this.config.repository}/actions/secrets/ELIA_GRAPHQL_TOKEN`, {
        method: 'PUT',
        headers: {
          'Authorization': 'token ' + this.config.githubToken,
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          encrypted_value: encodedToken
        })
      });

      console.log('📊 GitHub API response status:', response.status);
      
      if (response.status === 201) {
        console.log('✅ GitHub secret updated successfully');
        return true;
      } else if (response.status === 204) {
        console.log('✅ GitHub secret updated successfully (no content)');
        return true;
      } else {
        const errorText = await response.text();
        console.error('❌ GitHub API error:', response.status, errorText);
        this.addLog(`GitHub API error: ${response.status} - ${errorText}`, 'error');
        return false;
      }
    } catch (error) {
      console.error('❌ GitHub API request failed:', error);
      this.addLog('GitHub API request failed: ' + error.message, 'error');
      return false;
    }
  }

  async testGitHubConnection() {
    if (!this.config.githubToken || !this.config.repository) {
      return { success: false, error: 'GitHub configuration missing' };
    }

    try {
      console.log('🧪 Testing GitHub connection...');
      
      const response = await fetch(`https://api.github.com/repos/${this.config.repository}`, {
        headers: {
          'Authorization': 'token ' + this.config.githubToken,
          'Accept': 'application/vnd.github.v3+json'
        }
      });

      if (response.ok) {
        const repoData = await response.json();
        console.log('✅ GitHub connection successful:', repoData.full_name);
        return { success: true, repository: repoData.full_name };
      } else {
        const errorText = await response.text();
        console.error('❌ GitHub connection failed:', response.status, errorText);
        return { success: false, error: `${response.status}: ${errorText}` };
      }
    } catch (error) {
      console.error('❌ GitHub connection test failed:', error);
      return { success: false, error: error.message };
    }
  }

  showNotification(message, type = 'info') {
    console.log('🔔 Showing notification:', message, type);
    
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'Elia Token Manager',
      message: message
    });
  }

  addLog(message, type = 'info') {
    const logEntry = {
      timestamp: new Date().toLocaleString(),
      message: message,
      type: type
    };
    
    this.logs.unshift(logEntry);
    
    // Keep only last 100 logs
    if (this.logs.length > 100) {
      this.logs = this.logs.slice(0, 100);
    }
    
    // Save logs to storage
    chrome.storage.local.set({ logs: this.logs });
    
    console.log(`📝 [${type.toUpperCase()}] ${message}`);
  }
}

// Initialize the monitor when extension starts
console.log('🚀 Starting Elia Token Monitor...');
new EliaTokenMonitor();
