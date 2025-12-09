// Content Script - Elia Page Monitor
class EliaPageMonitor {
  constructor() {
    console.log('📄 Elia Page Monitor initialized');
    this.setupMessageListener();
    this.setupPageObserver();
    this.setupNetworkInterceptor();
    
    // Initial scan
    setTimeout(() => this.scanPageForTokens(), 1000);
  }

  setupMessageListener() {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      console.log('📨 Content script message:', request.action);
      
      if (request.action === 'checkToken') {
        console.log('🔍 Performing token scan...');
        this.scanPageForTokens();
        sendResponse({ success: true });
      }
    });
  }

  setupPageObserver() {
    console.log('👀 Setting up page observer...');
    
    // Wait for document.body to be available
    const setupObserver = () => {
      if (!document.body) {
        console.log('⏳ Waiting for document.body...');
        setTimeout(setupObserver, 100);
        return;
      }
      
      // Monitor DOM changes for token-related elements
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.type === 'childList') {
            this.checkForTokenElements(mutation.addedNodes);
          }
        });
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['data-token', 'data-auth']
      });
      
      console.log('✅ Page observer active');

      // Monitor URL changes (SPA navigation)
      let lastUrl = location.href;
      new MutationObserver(() => {
        const url = location.href;
        if (url !== lastUrl) {
          lastUrl = url;
          console.log('🔄 URL changed, scanning for tokens...');
          setTimeout(() => this.scanPageForTokens(), 1000);
        }
      }).observe(document, { subtree: true, childList: true });
    };
    
    setupObserver();
  }

  setupNetworkInterceptor() {
    console.log('🌐 Setting up network interceptor...');
    
    // Intercept fetch requests
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const response = await originalFetch.apply(this, args);
      
      // Check if this is an API call that might return tokens
      if (args[0] && args[0].includes && args[0].includes('graphql')) {
        try {
          const clonedResponse = response.clone();
          clonedResponse.json().then(data => {
            this.checkResponseForTokens(data);
          }).catch(() => {
            // Ignore JSON parsing errors
          });
        } catch (e) {
          // Ignore cloning errors
        }
      }
      
      return response;
    };

    // Intercept XMLHttpRequest
    const originalXHR = window.XMLHttpRequest;
    window.XMLHttpRequest = function() {
      const xhr = new originalXHR();
      const originalOpen = xhr.open;
      const originalSend = xhr.send;
      
      xhr.open = function(method, url, ...args) {
        this._url = url;
        return originalOpen.apply(this, [method, url, ...args]);
      };
      
      xhr.send = function(...args) {
        const originalOnReadyStateChange = this.onreadystatechange;
        
        this.onreadystatechange = function() {
          if (this.readyState === 4 && this._url && this._url.includes('graphql')) {
            try {
              const response = JSON.parse(this.responseText);
              this.checkResponseForTokens(response);
            } catch (e) {
              // Ignore parsing errors
            }
          }
          
          if (originalOnReadyStateChange) {
            originalOnReadyStateChange.apply(this, arguments);
          }
        }.bind(this);
        
        return originalSend.apply(this, args);
      };
      
      return xhr;
    };
  }

  checkResponseForTokens(data) {
    console.log('🔍 Checking API response for tokens...');
    
    // Look for tokens in GraphQL responses
    if (data && data.data) {
      const dataString = JSON.stringify(data.data);
      const tokenMatches = dataString.match(/eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*/g);
      
      if (tokenMatches) {
        tokenMatches.forEach(token => {
          if (this.isValidJWT(token)) {
            console.log('🎯 Token found in API response');
            chrome.runtime.sendMessage({ 
              action: 'tokenFound', 
              token: token,
              source: 'api_response'
            });
          }
        });
      }
    }
  }

  scanPageForTokens() {
    console.log('🔍 Scanning page for tokens...');
    
    let tokensFound = 0;
    
    // Check localStorage
    tokensFound += this.checkLocalStorage();
    
    // Check sessionStorage
    tokensFound += this.checkSessionStorage();
    
    // Check cookies
    tokensFound += this.checkCookies();
    
    // Check global variables
    tokensFound += this.checkGlobalVariables();
    
    // Check script tags
    tokensFound += this.checkScriptTags();
    
    // Check meta tags
    tokensFound += this.checkMetaTags();
    
    console.log(`📊 Token scan complete: ${tokensFound} tokens found`);
  }

  checkLocalStorage() {
    let tokensFound = 0;
    
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (this.isTokenKey(key)) {
          const value = localStorage.getItem(key);
          if (this.isValidJWT(value)) {
            console.log(`🔑 Token found in localStorage: ${key}`);
            chrome.runtime.sendMessage({ 
              action: 'tokenFound', 
              token: value,
              source: 'localStorage-' + key
            });
            tokensFound++;
          }
        }
      }
    } catch (e) {
      console.warn('⚠️ Error accessing localStorage:', e);
    }
    
    return tokensFound;
  }

  checkSessionStorage() {
    let tokensFound = 0;
    
    try {
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (this.isTokenKey(key)) {
          const value = sessionStorage.getItem(key);
          if (this.isValidJWT(value)) {
            console.log(`🔑 Token found in sessionStorage: ${key}`);
            chrome.runtime.sendMessage({ 
              action: 'tokenFound', 
              token: value,
              source: 'sessionStorage-' + key
            });
            tokensFound++;
          }
        }
      }
    } catch (e) {
      console.warn('⚠️ Error accessing sessionStorage:', e);
    }
    
    return tokensFound;
  }

  checkCookies() {
    let tokensFound = 0;
    
    try {
      const cookies = document.cookie.split(';');
      cookies.forEach(cookie => {
        const [name, value] = cookie.trim().split('=');
        if (name && this.isTokenKey(name)) {
          if (this.isValidJWT(value)) {
            console.log(`🔑 Token found in cookie: ${name}`);
            chrome.runtime.sendMessage({ 
              action: 'tokenFound', 
              token: value,
              source: 'cookie-' + name
            });
            tokensFound++;
          }
        }
      });
    } catch (e) {
      console.warn('⚠️ Error accessing cookies:', e);
    }
    
    return tokensFound;
  }

  checkGlobalVariables() {
    let tokensFound = 0;
    
    // Check common global variable names for tokens
    const tokenVars = [
      'token', 'authToken', 'jwtToken', 'eliaToken', 'accessToken',
      'bearerToken', 'sessionToken', 'userToken', 'apiToken'
    ];
    
    tokenVars.forEach(varName => {
      if (window[varName] && this.isValidJWT(window[varName])) {
        console.log(`🔑 Token found in global variable: ${varName}`);
        chrome.runtime.sendMessage({ 
          action: 'tokenFound', 
          token: window[varName],
          source: 'global-' + varName
        });
        tokensFound++;
      }
    });
    
    // Check nested objects
    const nestedPaths = [
      'window.app.token', 'window.app.authToken', 'window.app.accessToken',
      'window.elia.token', 'window.elia.authToken', 'window.elia.accessToken',
      'window.user.token', 'window.user.authToken', 'window.user.accessToken'
    ];
    
    nestedPaths.forEach(path => {
      try {
        const value = this.getNestedValue(path);
        if (value && this.isValidJWT(value)) {
          console.log(`🔑 Token found in nested path: ${path}`);
          chrome.runtime.sendMessage({ 
            action: 'tokenFound', 
            token: value,
            source: 'nested-' + path
          });
          tokensFound++;
        }
      } catch (e) {
        // Ignore access errors
      }
    });
    
    return tokensFound;
  }

  checkScriptTags() {
    let tokensFound = 0;
    
    const scripts = document.querySelectorAll('script');
    scripts.forEach(script => {
      if (script.textContent) {
        // Look for JWT tokens in script content
        const tokenMatches = script.textContent.match(/eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*/g);
        
        if (tokenMatches) {
          tokenMatches.forEach(token => {
            if (this.isValidJWT(token)) {
              console.log('🔑 Token found in script tag');
              chrome.runtime.sendMessage({ 
                action: 'tokenFound', 
                token: token,
                source: 'script-tag'
              });
              tokensFound++;
            }
          });
        }
      }
    });
    
    return tokensFound;
  }

  checkMetaTags() {
    let tokensFound = 0;
    
    const metas = document.querySelectorAll('meta');
    metas.forEach(meta => {
      const name = meta.getAttribute('name') || meta.getAttribute('property');
      const content = meta.getAttribute('content');
      
      if (name && content && this.isTokenKey(name)) {
        if (this.isValidJWT(content)) {
          console.log(`🔑 Token found in meta tag: ${name}`);
          chrome.runtime.sendMessage({ 
            action: 'tokenFound', 
            token: content,
            source: 'meta-' + name
          });
          tokensFound++;
        }
      }
    });
    
    return tokensFound;
  }

  checkForTokenElements(nodes) {
    nodes.forEach(node => {
      if (node.nodeType === Node.ELEMENT_NODE) {
        // Check data attributes
        if (node.dataset) {
          ['token', 'authToken', 'accessToken', 'jwtToken'].forEach(attr => {
            if (node.dataset[attr] && this.isValidJWT(node.dataset[attr])) {
              console.log(`🔑 Token found in data-${attr}`);
              chrome.runtime.sendMessage({ 
                action: 'tokenFound', 
                token: node.dataset[attr],
                source: `data-${attr}`
              });
            }
          });
        }

        // Check hidden inputs
        if (node.tagName === 'INPUT' && node.type === 'hidden' && node.value) {
          if (this.isValidJWT(node.value)) {
            console.log('🔑 Token found in hidden input');
            chrome.runtime.sendMessage({ 
              action: 'tokenFound', 
              token: node.value,
              source: 'hidden-input'
            });
          }
        }

        // Check script tags for dynamic content
        if (node.tagName === 'SCRIPT' && node.textContent) {
          const tokenMatches = node.textContent.match(/eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*/g);
          if (tokenMatches) {
            tokenMatches.forEach(token => {
              if (this.isValidJWT(token)) {
                console.log('🔑 Token found in dynamic script');
                chrome.runtime.sendMessage({ 
                  action: 'tokenFound', 
                  token: token,
                  source: 'dynamic-script'
                });
              }
            });
          }
        }
      }
    });
  }

  getNestedValue(path) {
    return path.split('.').reduce((obj, key) => obj && obj[key], window);
  }

  isTokenKey(key) {
    if (!key || typeof key !== 'string') return false;
    
    const tokenPatterns = [
      /token/i, /auth/i, /jwt/i, /elia/i, /access/i, /bearer/i,
      /session/i, /user/i, /api/i, /credential/i
    ];
    
    return tokenPatterns.some(pattern => pattern.test(key));
  }

  isValidJWT(str) {
    if (!str || typeof str !== 'string') return false;
    
    const parts = str.split('.');
    if (parts.length !== 3) return false;
    
    try {
      // Try to decode header and payload
      JSON.parse(atob(parts[0]));
      const payload = JSON.parse(atob(parts[1]));
      
      // Check for required JWT fields
      return payload && (payload.exp || payload.iat || payload.sub);
    } catch (e) {
      return false;
    }
  }
}

// Initialize the page monitor
console.log('🚀 Starting Elia Page Monitor...');
new EliaPageMonitor();
