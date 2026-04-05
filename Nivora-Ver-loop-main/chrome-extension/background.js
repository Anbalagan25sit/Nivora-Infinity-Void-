// Background service worker for Nivora Chrome Extension
// Handles LiveKit connection and extension state

let isAssistantOpen = false;

// Extension configuration
const CONFIG = {
  LIVEKIT_URL: '',
  API_ENDPOINT: 'http://localhost:8080/api/token',
};

// Load config from storage on startup
chrome.storage.sync.get(['livekitUrl', 'apiEndpoint'], (result) => {
  CONFIG.LIVEKIT_URL = result.livekitUrl || '';
  CONFIG.API_ENDPOINT = result.apiEndpoint || 'http://localhost:8080/api/token';
  console.log('Config loaded:', CONFIG);
});

// Listen for messages from popup and content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Message received:', request.action);

  switch (request.action) {
    case 'getToken':
      // Fetch LiveKit token from server
      fetchToken(request.roomName, request.participantName)
        .then(token => sendResponse({ success: true, token }))
        .catch(error => sendResponse({ success: false, error: error.message }));
      return true; // Keep channel open for async response

    case 'getConfig':
      // Return current config
      chrome.storage.sync.get(['livekitUrl', 'apiEndpoint'], (result) => {
        sendResponse({
          success: true,
          config: {
            LIVEKIT_URL: result.livekitUrl || '',
            API_ENDPOINT: result.apiEndpoint || 'http://localhost:8080/api/token'
          }
        });
      });
      return true;

    case 'saveConfig':
      chrome.storage.sync.set({
        livekitUrl: request.livekitUrl,
        apiEndpoint: request.apiEndpoint
      }, () => {
        CONFIG.LIVEKIT_URL = request.livekitUrl;
        CONFIG.API_ENDPOINT = request.apiEndpoint;
        console.log('Config saved:', CONFIG);
        sendResponse({ success: true });
      });
      return true;

    case 'toggleAssistant':
      // Forward to content script in active tab
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0] && tabs[0].id) {
          chrome.tabs.sendMessage(tabs[0].id, {
            action: 'toggleAssistant',
            isOpen: request.isOpen
          }).catch(err => {
            console.log('Content script not ready:', err);
          });
        }
        sendResponse({ success: true });
      });
      return true;

    case 'captureScreen':
      // Capture current tab as image for vision analysis
      chrome.tabs.captureVisibleTab(null, { format: 'png' }, (dataUrl) => {
        if (chrome.runtime.lastError) {
          sendResponse({ success: false, error: chrome.runtime.lastError.message });
        } else {
          sendResponse({ success: true, screenshot: dataUrl });
        }
      });
      return true;
  }
});

// Fetch LiveKit token from token server
async function fetchToken(roomName, participantName) {
  const apiEndpoint = CONFIG.API_ENDPOINT || 'http://localhost:8080/api/token';
  const response = await fetch(`${apiEndpoint}?room=${roomName}&participant=${participantName}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch token: ${response.status}`);
  }
  const data = await response.json();
  return data.token;
}

// Handle keyboard shortcut
chrome.commands?.onCommand?.addListener((command) => {
  if (command === 'toggle-assistant') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0] && tabs[0].id) {
        isAssistantOpen = !isAssistantOpen;
        chrome.tabs.sendMessage(tabs[0].id, {
          action: 'toggleAssistant',
          isOpen: isAssistantOpen
        }).catch(err => {
          console.log('Content script not ready:', err);
        });
      }
    });
  }
});

console.log('Nivora Background Service Worker loaded');
