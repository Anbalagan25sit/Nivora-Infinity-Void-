// Nivora Chrome Extension - Popup Settings Script

document.addEventListener('DOMContentLoaded', () => {
  const livekitUrlInput = document.getElementById('livekit-url');
  const apiEndpointInput = document.getElementById('api-endpoint');
  const saveBtn = document.getElementById('save-btn');
  const testBtn = document.getElementById('test-btn');
  const statusDiv = document.getElementById('status');

  // Load saved settings directly from storage
  chrome.storage.sync.get(['livekitUrl', 'apiEndpoint'], (result) => {
    livekitUrlInput.value = result.livekitUrl || '';
    apiEndpointInput.value = result.apiEndpoint || 'http://localhost:8080/api/token';
    console.log('Settings loaded:', result);
  });

  // Save settings
  saveBtn.addEventListener('click', () => {
    const livekitUrl = livekitUrlInput.value.trim();
    const apiEndpoint = apiEndpointInput.value.trim();

    if (!livekitUrl) {
      showStatus('Please enter LiveKit Server URL', 'error');
      return;
    }

    if (!apiEndpoint) {
      showStatus('Please enter Token API Endpoint', 'error');
      return;
    }

    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';

    // Save directly to storage
    chrome.storage.sync.set({
      livekitUrl: livekitUrl,
      apiEndpoint: apiEndpoint
    }, () => {
      saveBtn.disabled = false;
      saveBtn.textContent = 'Save Settings';

      if (chrome.runtime.lastError) {
        showStatus('Error saving: ' + chrome.runtime.lastError.message, 'error');
      } else {
        showStatus('Settings saved successfully!', 'success');
        console.log('Settings saved:', { livekitUrl, apiEndpoint });
      }
    });
  });

  // Test connection
  testBtn.addEventListener('click', async () => {
    const apiEndpoint = apiEndpointInput.value.trim();

    if (!apiEndpoint) {
      showStatus('Please enter Token API Endpoint first', 'error');
      return;
    }

    testBtn.disabled = true;
    testBtn.textContent = 'Testing...';

    try {
      // Test the token endpoint
      const response = await fetch(`${apiEndpoint}?room=test&participant=test-user`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data.token) {
        showStatus('Connection successful! Token server is working.', 'success');
      } else if (data.error) {
        showStatus('Server error: ' + data.error, 'error');
      } else {
        showStatus('Token server responded but no token received', 'error');
      }
    } catch (error) {
      console.error('Connection test failed:', error);
      showStatus(`Connection failed: ${error.message}. Is the token server running?`, 'error');
    } finally {
      testBtn.disabled = false;
      testBtn.textContent = 'Test Connection';
    }
  });

  function showStatus(message, type) {
    statusDiv.textContent = message;
    statusDiv.className = 'status ' + type;

    // Auto-hide success messages after 3 seconds
    if (type === 'success') {
      setTimeout(() => {
        statusDiv.className = 'status';
      }, 3000);
    }
  }
});
