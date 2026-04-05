// Content script for Nivora Chrome Extension
// Injects the voice assistant UI into web pages with LiveKit integration

(function() {
  'use strict';

  // Prevent multiple injections
  if (window.nivoraInjected) return;
  window.nivoraInjected = true;

  // Configuration
  let config = {
    livekitUrl: 'wss://nivora-5opea2lo.livekit.cloud',
    apiEndpoint: 'http://localhost:8080/api/token'
  };

  // State
  let isOpen = false;
  let isConnected = false;
  let isListening = false;
  let isSpeaking = false;
  let audioContext = null;
  let analyser = null;
  let mediaStream = null;
  let livekitRoom = null;
  let LivekitClient = null;

  // Create container element
  const container = document.createElement('div');
  container.id = 'nivora-assistant-container';
  container.innerHTML = `
    <div class="nivora-assistant" id="nivora-assistant">
      <!-- Floating Button (when closed) -->
      <button class="nivora-fab" id="nivora-fab" title="Open Nivora Assistant">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
          <line x1="12" y1="19" x2="12" y2="22"/>
        </svg>
      </button>

      <!-- Main Panel -->
      <div class="nivora-panel hidden" id="nivora-panel">
        <!-- Header -->
        <div class="nivora-header">
          <div class="nivora-logo">
            <svg viewBox="0 0 24 24" fill="currentColor" class="nivora-icon">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            <span>Nivora</span>
          </div>
          <div class="nivora-connection-status" id="nivora-connection-status">
            <span class="nivora-status-dot"></span>
            <span class="nivora-status-text">Disconnected</span>
          </div>
          <div class="nivora-header-actions">
            <button class="nivora-btn-icon" id="nivora-settings-btn" title="Settings">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
            </button>
            <button class="nivora-btn-icon" id="nivora-close-btn" title="Close">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Transcript Area -->
        <div class="nivora-transcript" id="nivora-transcript">
          <div class="nivora-welcome">
            <div class="nivora-avatar">
              <svg viewBox="0 0 100 100" class="nivora-visualizer-placeholder">
                <circle cx="50" cy="50" r="40" fill="none" stroke="currentColor" stroke-width="2" opacity="0.3"/>
              </svg>
            </div>
            <p class="nivora-status" id="nivora-status">Click Connect to start</p>
          </div>
        </div>

        <!-- Audio Visualizer -->
        <div class="nivora-visualizer-container" id="nivora-visualizer-container">
          <canvas id="nivora-visualizer" width="200" height="200"></canvas>
        </div>

        <!-- Controls -->
        <div class="nivora-controls">
          <button class="nivora-control-btn nivora-cancel-btn hidden" id="nivora-cancel-btn" title="Disconnect">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
          <button class="nivora-control-btn nivora-connect-btn" id="nivora-connect-btn" title="Connect to Nivora">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
            </svg>
          </button>
          <button class="nivora-control-btn nivora-mic-btn hidden" id="nivora-mic-btn" title="Push to talk">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              <line x1="12" y1="19" x2="12" y2="22"/>
            </svg>
          </button>
        </div>

        <!-- Text Input -->
        <div class="nivora-input-container">
          <div class="nivora-input-wrapper">
            <button class="nivora-attach-btn" id="nivora-attach-btn" title="Attach page context">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
            </button>
            <input type="text" class="nivora-input" id="nivora-input" placeholder="Ask anything..." disabled>
            <button class="nivora-send-btn" id="nivora-send-btn" title="Send" disabled>
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Settings Modal -->
      <div class="nivora-modal hidden" id="nivora-settings-modal">
        <div class="nivora-modal-content">
          <div class="nivora-modal-header">
            <h3>Settings</h3>
            <button class="nivora-btn-icon" id="nivora-settings-close">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          <div class="nivora-modal-body">
            <div class="nivora-form-group">
              <label for="nivora-livekit-url">LiveKit Server URL</label>
              <input type="text" id="nivora-livekit-url" placeholder="wss://your-server.livekit.cloud">
            </div>
            <div class="nivora-form-group">
              <label for="nivora-api-endpoint">Token API Endpoint</label>
              <input type="text" id="nivora-api-endpoint" placeholder="http://localhost:8080/api/token">
            </div>
            <button class="nivora-btn-primary" id="nivora-save-settings">Save Settings</button>
          </div>
        </div>
      </div>
    </div>
  `;

  // Inject styles
  const styles = document.createElement('link');
  styles.rel = 'stylesheet';
  styles.href = chrome.runtime.getURL('styles/content.css');
  document.head.appendChild(styles);

  // Inject container
  document.body.appendChild(container);

  // Get DOM elements
  const fab = document.getElementById('nivora-fab');
  const panel = document.getElementById('nivora-panel');
  const closeBtn = document.getElementById('nivora-close-btn');
  const settingsBtn = document.getElementById('nivora-settings-btn');
  const settingsModal = document.getElementById('nivora-settings-modal');
  const settingsClose = document.getElementById('nivora-settings-close');
  const saveSettings = document.getElementById('nivora-save-settings');
  const connectBtn = document.getElementById('nivora-connect-btn');
  const micBtn = document.getElementById('nivora-mic-btn');
  const cancelBtn = document.getElementById('nivora-cancel-btn');
  const input = document.getElementById('nivora-input');
  const sendBtn = document.getElementById('nivora-send-btn');
  const attachBtn = document.getElementById('nivora-attach-btn');
  const transcriptEl = document.getElementById('nivora-transcript');
  const status = document.getElementById('nivora-status');
  const visualizerCanvas = document.getElementById('nivora-visualizer');
  const connectionStatus = document.getElementById('nivora-connection-status');

  // Load config from storage
  chrome.storage.sync.get(['livekitUrl', 'apiEndpoint'], (result) => {
    if (result.livekitUrl) config.livekitUrl = result.livekitUrl;
    if (result.apiEndpoint) config.apiEndpoint = result.apiEndpoint;
    document.getElementById('nivora-livekit-url').value = config.livekitUrl;
    document.getElementById('nivora-api-endpoint').value = config.apiEndpoint;
  });

  // Load LiveKit SDK
  async function loadLiveKitSDK() {
    if (LivekitClient) return LivekitClient;

    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/livekit-client@2.0.0/dist/livekit-client.umd.min.js';
      script.onload = () => {
        LivekitClient = window.LivekitClient;
        console.log('LiveKit SDK loaded');
        resolve(LivekitClient);
      };
      script.onerror = () => reject(new Error('Failed to load LiveKit SDK'));
      document.head.appendChild(script);
    });
  }

  // Toggle assistant panel
  function togglePanel(show) {
    isOpen = show !== undefined ? show : !isOpen;
    if (isOpen) {
      fab.classList.add('hidden');
      panel.classList.remove('hidden');
      initVisualizer();
    } else {
      fab.classList.remove('hidden');
      panel.classList.add('hidden');
    }
  }

  // Update connection status UI
  function updateConnectionStatus(connected, text) {
    isConnected = connected;
    const dot = connectionStatus.querySelector('.nivora-status-dot');
    const statusText = connectionStatus.querySelector('.nivora-status-text');

    if (connected) {
      dot.style.background = '#2dd4bf';
      statusText.textContent = text || 'Connected';
      connectBtn.classList.add('hidden');
      micBtn.classList.remove('hidden');
      cancelBtn.classList.remove('hidden');
      input.disabled = false;
      sendBtn.disabled = false;
    } else {
      dot.style.background = '#ef4444';
      statusText.textContent = text || 'Disconnected';
      connectBtn.classList.remove('hidden');
      micBtn.classList.add('hidden');
      cancelBtn.classList.add('hidden');
      input.disabled = true;
      sendBtn.disabled = true;
    }
  }

  // Connect to LiveKit
  async function connectToLiveKit() {
    try {
      status.textContent = 'Loading LiveKit...';
      updateConnectionStatus(false, 'Connecting...');

      // Load SDK
      await loadLiveKitSDK();

      // Get token from server
      status.textContent = 'Getting token...';
      const participantId = 'user-' + Math.random().toString(36).substr(2, 9);
      const tokenResponse = await fetch(
        `${config.apiEndpoint}?room=nivora-assistant&participant=${participantId}`
      );

      if (!tokenResponse.ok) {
        throw new Error(`Token server error: ${tokenResponse.status}`);
      }

      const tokenData = await tokenResponse.json();
      console.log('Token received:', tokenData);

      // Create room
      status.textContent = 'Connecting to room...';
      livekitRoom = new LivekitClient.Room({
        adaptiveStream: true,
        dynacast: true,
        audioCaptureDefaults: {
          autoGainControl: true,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      // Set up event handlers
      setupRoomEvents();

      // Connect
      await livekitRoom.connect(config.livekitUrl, tokenData.token);

      console.log('Connected to room:', livekitRoom.name);
      status.textContent = 'Connected! Click mic to speak';
      updateConnectionStatus(true, 'Connected');
      addMessage('system', 'Connected to Nivora. Click the microphone to speak.');

    } catch (error) {
      console.error('Connection error:', error);
      status.textContent = 'Connection failed';
      updateConnectionStatus(false, 'Error');
      addMessage('system', `Connection failed: ${error.message}`);
    }
  }

  // Setup LiveKit room events
  function setupRoomEvents() {
    if (!livekitRoom) return;

    // Track subscribed (agent audio)
    livekitRoom.on(LivekitClient.RoomEvent.TrackSubscribed, (track, publication, participant) => {
      console.log('Track subscribed:', track.kind, participant.identity);

      if (track.kind === LivekitClient.Track.Kind.Audio) {
        const audioEl = track.attach();
        audioEl.id = 'nivora-agent-audio-' + participant.identity;
        document.body.appendChild(audioEl);
        isSpeaking = true;
        status.textContent = 'Nivora is speaking...';
      }
    });

    // Track unsubscribed
    livekitRoom.on(LivekitClient.RoomEvent.TrackUnsubscribed, (track) => {
      track.detach().forEach(el => el.remove());
      isSpeaking = false;
      status.textContent = 'Click mic to speak';
    });

    // Data received (transcripts, messages)
    livekitRoom.on(LivekitClient.RoomEvent.DataReceived, (payload, participant) => {
      try {
        const decoder = new TextDecoder();
        const message = JSON.parse(decoder.decode(payload));
        console.log('Data received:', message);

        if (message.type === 'transcript') {
          if (message.participant === livekitRoom.localParticipant?.identity) {
            // User transcript
            addMessage('user', message.text);
          } else {
            // Agent transcript
            addMessage('assistant', message.text);
          }
        }
      } catch (e) {
        console.error('Error parsing data:', e);
      }
    });

    // Participant connected
    livekitRoom.on(LivekitClient.RoomEvent.ParticipantConnected, (participant) => {
      console.log('Participant connected:', participant.identity);
      if (participant.identity.includes('agent') || participant.identity.includes('nivora')) {
        addMessage('system', 'Nivora agent connected');
      }
    });

    // Disconnected
    livekitRoom.on(LivekitClient.RoomEvent.Disconnected, () => {
      console.log('Disconnected from room');
      updateConnectionStatus(false, 'Disconnected');
      status.textContent = 'Disconnected';
      addMessage('system', 'Disconnected from Nivora');
    });
  }

  // Disconnect from LiveKit
  async function disconnect() {
    if (livekitRoom) {
      await livekitRoom.disconnect();
      livekitRoom = null;
    }
    stopListening();
    updateConnectionStatus(false);
    status.textContent = 'Click Connect to start';
  }

  // Start listening (publish microphone)
  async function startListening() {
    if (!livekitRoom || !isConnected) {
      addMessage('system', 'Please connect first');
      return;
    }

    try {
      // Enable microphone
      await livekitRoom.localParticipant.setMicrophoneEnabled(true);

      // Get audio track for visualizer
      const audioTracks = livekitRoom.localParticipant.audioTrackPublications;
      if (audioTracks.size > 0) {
        const publication = audioTracks.values().next().value;
        if (publication.track) {
          setupAudioAnalyser(publication.track.mediaStreamTrack);
        }
      }

      isListening = true;
      micBtn.classList.add('listening');
      status.textContent = 'Listening...';

    } catch (error) {
      console.error('Microphone error:', error);
      addMessage('system', 'Microphone access denied');
    }
  }

  // Stop listening
  async function stopListening() {
    if (livekitRoom && livekitRoom.localParticipant) {
      await livekitRoom.localParticipant.setMicrophoneEnabled(false);
    }

    if (audioContext) {
      audioContext.close();
      audioContext = null;
      analyser = null;
    }

    isListening = false;
    micBtn.classList.remove('listening');
    if (isConnected) {
      status.textContent = 'Click mic to speak';
    }
  }

  // Setup audio analyser for visualizer
  function setupAudioAnalyser(mediaStreamTrack) {
    try {
      audioContext = new AudioContext();
      analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;

      const stream = new MediaStream([mediaStreamTrack]);
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
    } catch (e) {
      console.error('Audio analyser setup error:', e);
    }
  }

  // Audio Visualizer
  function initVisualizer() {
    const ctx = visualizerCanvas.getContext('2d');
    const centerX = visualizerCanvas.width / 2;
    const centerY = visualizerCanvas.height / 2;
    const radius = 60;
    const barCount = 64;

    function draw() {
      ctx.clearRect(0, 0, visualizerCanvas.width, visualizerCanvas.height);

      // Draw base circle
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
      ctx.strokeStyle = isConnected ? 'rgba(45, 212, 191, 0.3)' : 'rgba(161, 161, 170, 0.3)';
      ctx.lineWidth = 2;
      ctx.stroke();

      if (analyser && isListening) {
        // User speaking - teal color
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyser.getByteFrequencyData(dataArray);

        for (let i = 0; i < barCount; i++) {
          const angle = (i / barCount) * Math.PI * 2 - Math.PI / 2;
          const barIndex = Math.floor((i / barCount) * bufferLength);
          const barHeight = (dataArray[barIndex] / 255) * 40 + 5;

          const x1 = centerX + Math.cos(angle) * radius;
          const y1 = centerY + Math.sin(angle) * radius;
          const x2 = centerX + Math.cos(angle) * (radius + barHeight);
          const y2 = centerY + Math.sin(angle) * (radius + barHeight);

          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
          ctx.strokeStyle = `rgba(45, 212, 191, ${0.5 + (dataArray[barIndex] / 255) * 0.5})`;
          ctx.lineWidth = 2;
          ctx.lineCap = 'round';
          ctx.stroke();
        }
      } else if (isSpeaking) {
        // AI speaking - purple color
        const time = Date.now() / 1000;
        for (let i = 0; i < barCount; i++) {
          const angle = (i / barCount) * Math.PI * 2 - Math.PI / 2;
          const barHeight = Math.sin(time * 3 + i * 0.2) * 15 + 20;

          const x1 = centerX + Math.cos(angle) * radius;
          const y1 = centerY + Math.sin(angle) * radius;
          const x2 = centerX + Math.cos(angle) * (radius + barHeight);
          const y2 = centerY + Math.sin(angle) * (radius + barHeight);

          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
          ctx.strokeStyle = `rgba(147, 51, 234, ${0.5 + Math.sin(time * 3 + i * 0.2) * 0.3})`;
          ctx.lineWidth = 2;
          ctx.lineCap = 'round';
          ctx.stroke();
        }
      } else if (isConnected) {
        // Connected but idle - gentle pulse
        const time = Date.now() / 1000;
        const pulse = Math.sin(time * 2) * 0.1 + 0.9;

        for (let i = 0; i < 50; i++) {
          const angle = (i / 50) * Math.PI * 2 + time * 0.5;
          const dist = radius * pulse + Math.sin(time * 2 + i) * 10;
          const x = centerX + Math.cos(angle) * dist;
          const y = centerY + Math.sin(angle) * dist;
          const size = 2 + Math.sin(time + i) * 1;

          ctx.beginPath();
          ctx.arc(x, y, size, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(45, 212, 191, ${0.3 + Math.sin(time + i) * 0.2})`;
          ctx.fill();
        }
      } else {
        // Disconnected - gray pulse
        const time = Date.now() / 1000;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius + Math.sin(time) * 5, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(161, 161, 170, 0.2)';
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      requestAnimationFrame(draw);
    }

    draw();
  }

  // Add message to transcript
  function addMessage(role, text) {
    const welcome = transcriptEl.querySelector('.nivora-welcome');
    if (welcome && role !== 'system') {
      welcome.style.display = 'none';
    }

    const messageEl = document.createElement('div');
    messageEl.className = `nivora-message nivora-message-${role}`;

    if (role === 'user') {
      messageEl.innerHTML = `
        <div class="nivora-message-content">
          <span class="nivora-message-label">You</span>
          <p>${escapeHtml(text)}</p>
        </div>
      `;
    } else if (role === 'assistant') {
      messageEl.innerHTML = `
        <div class="nivora-message-content">
          <span class="nivora-message-label">Nivora</span>
          <p>${escapeHtml(text)}</p>
        </div>
      `;
    } else {
      messageEl.innerHTML = `<p class="nivora-system-message">${escapeHtml(text)}</p>`;
    }

    transcriptEl.appendChild(messageEl);
    transcriptEl.scrollTop = transcriptEl.scrollHeight;
  }

  // Send text message via data channel
  async function sendTextMessage(text) {
    if (!livekitRoom || !isConnected) {
      addMessage('system', 'Please connect first');
      return;
    }

    addMessage('user', text);

    try {
      const encoder = new TextEncoder();
      const data = encoder.encode(JSON.stringify({
        type: 'chat',
        text: text,
        timestamp: Date.now()
      }));

      await livekitRoom.localParticipant.publishData(data, { reliable: true });
      status.textContent = 'Message sent...';

    } catch (error) {
      console.error('Send error:', error);
      addMessage('system', 'Failed to send message');
    }
  }

  // Extract page content for context
  function extractPageContent() {
    return {
      title: document.title,
      url: window.location.href,
      description: document.querySelector('meta[name="description"]')?.content || '',
      content: document.body.innerText.substring(0, 3000)
    };
  }

  // Escape HTML
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Event listeners
  fab.addEventListener('click', () => togglePanel(true));
  closeBtn.addEventListener('click', () => togglePanel(false));

  // Connect button
  connectBtn.addEventListener('click', connectToLiveKit);

  // Cancel/Disconnect button
  cancelBtn.addEventListener('click', disconnect);

  // Microphone button
  micBtn.addEventListener('click', () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  });

  // Settings modal
  settingsBtn.addEventListener('click', () => {
    settingsModal.classList.remove('hidden');
  });
  settingsClose.addEventListener('click', () => {
    settingsModal.classList.add('hidden');
  });
  saveSettings.addEventListener('click', () => {
    const livekitUrl = document.getElementById('nivora-livekit-url').value;
    const apiEndpoint = document.getElementById('nivora-api-endpoint').value;

    chrome.storage.sync.set({ livekitUrl, apiEndpoint }, () => {
      config.livekitUrl = livekitUrl;
      config.apiEndpoint = apiEndpoint;
      settingsModal.classList.add('hidden');
      addMessage('system', 'Settings saved!');
    });
  });

  // Text input
  input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && input.value.trim()) {
      sendTextMessage(input.value.trim());
      input.value = '';
    }
  });

  sendBtn.addEventListener('click', () => {
    if (input.value.trim()) {
      sendTextMessage(input.value.trim());
      input.value = '';
    }
  });

  // Attach page context
  attachBtn.addEventListener('click', async () => {
    const context = extractPageContent();
    addMessage('system', `Page context: "${context.title}"`);
    input.value = `[About this page: ${context.title}] ` + input.value;
    input.focus();
  });

  // Listen for messages from background script
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'toggleAssistant') {
      togglePanel(request.isOpen);
    }
  });

  console.log('Nivora Assistant injected and ready');
})();
