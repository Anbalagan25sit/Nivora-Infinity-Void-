// Nivora Chrome Extension - LiveKit Integration Module
// Handles real-time voice communication with LiveKit server

class NivoraLiveKit {
  constructor() {
    this.room = null;
    this.localParticipant = null;
    this.audioTrack = null;
    this.isConnected = false;
    this.isPublishing = false;

    // Configuration
    this.config = {
      serverUrl: '',
      token: '',
      roomName: 'nivora-assistant'
    };

    // Callbacks
    this.onConnectionChange = null;
    this.onAgentMessage = null;
    this.onAgentSpeaking = null;
    this.onTranscript = null;
    this.onError = null;
  }

  // Initialize LiveKit SDK (dynamically loaded)
  async loadSDK() {
    if (window.LivekitClient) {
      return window.LivekitClient;
    }

    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/livekit-client/dist/livekit-client.umd.min.js';
      script.onload = () => {
        if (window.LivekitClient) {
          resolve(window.LivekitClient);
        } else {
          reject(new Error('LiveKit SDK failed to load'));
        }
      };
      script.onerror = () => reject(new Error('Failed to load LiveKit SDK'));
      document.head.appendChild(script);
    });
  }

  // Get token from server
  async getToken(roomName, participantName) {
    try {
      const response = await new Promise((resolve, reject) => {
        chrome.runtime.sendMessage({
          action: 'getToken',
          roomName: roomName || this.config.roomName,
          participantName: participantName || `user-${Date.now()}`
        }, (response) => {
          if (chrome.runtime.lastError) {
            reject(chrome.runtime.lastError);
          } else {
            resolve(response);
          }
        });
      });

      if (response.success) {
        return response.token;
      } else {
        throw new Error(response.error || 'Failed to get token');
      }
    } catch (error) {
      console.error('Token fetch error:', error);
      throw error;
    }
  }

  // Connect to LiveKit room
  async connect(serverUrl, token) {
    try {
      const lk = await this.loadSDK();

      // Create room
      this.room = new lk.Room({
        adaptiveStream: true,
        dynacast: true,
        audioCaptureDefaults: {
          autoGainControl: true,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      // Set up event handlers
      this.setupEventHandlers(lk);

      // Connect to room
      await this.room.connect(serverUrl, token);

      this.localParticipant = this.room.localParticipant;
      this.isConnected = true;

      if (this.onConnectionChange) {
        this.onConnectionChange(true);
      }

      console.log('Connected to LiveKit room:', this.room.name);
      return true;

    } catch (error) {
      console.error('LiveKit connection error:', error);
      this.isConnected = false;

      if (this.onError) {
        this.onError(error);
      }

      throw error;
    }
  }

  // Set up LiveKit event handlers
  setupEventHandlers(lk) {
    // Connection state changes
    this.room.on(lk.RoomEvent.ConnectionStateChanged, (state) => {
      console.log('Connection state:', state);
      this.isConnected = state === lk.ConnectionState.Connected;

      if (this.onConnectionChange) {
        this.onConnectionChange(this.isConnected);
      }
    });

    // Track subscribed (agent audio)
    this.room.on(lk.RoomEvent.TrackSubscribed, (track, publication, participant) => {
      if (track.kind === lk.Track.Kind.Audio && participant.identity !== this.localParticipant?.identity) {
        // Agent audio track
        const audioElement = track.attach();
        audioElement.id = 'nivora-agent-audio';
        document.body.appendChild(audioElement);

        console.log('Agent audio track attached');

        if (this.onAgentSpeaking) {
          this.onAgentSpeaking(true);
        }
      }
    });

    // Track unsubscribed
    this.room.on(lk.RoomEvent.TrackUnsubscribed, (track, publication, participant) => {
      track.detach().forEach(el => el.remove());

      if (this.onAgentSpeaking) {
        this.onAgentSpeaking(false);
      }
    });

    // Data received (chat/transcript messages)
    this.room.on(lk.RoomEvent.DataReceived, (payload, participant) => {
      try {
        const decoder = new TextDecoder();
        const message = JSON.parse(decoder.decode(payload));

        console.log('Data received:', message);

        if (message.type === 'transcript' && this.onTranscript) {
          this.onTranscript(message.text, message.role || 'assistant');
        }

        if (message.type === 'message' && this.onAgentMessage) {
          this.onAgentMessage(message.text);
        }
      } catch (e) {
        console.error('Error parsing data message:', e);
      }
    });

    // Participant connected
    this.room.on(lk.RoomEvent.ParticipantConnected, (participant) => {
      console.log('Participant connected:', participant.identity);
    });

    // Disconnected
    this.room.on(lk.RoomEvent.Disconnected, () => {
      console.log('Disconnected from room');
      this.isConnected = false;

      if (this.onConnectionChange) {
        this.onConnectionChange(false);
      }
    });
  }

  // Start publishing audio (push to talk)
  async startPublishing() {
    if (!this.isConnected || !this.localParticipant) {
      throw new Error('Not connected to room');
    }

    try {
      // Enable microphone
      await this.localParticipant.setMicrophoneEnabled(true);
      this.isPublishing = true;

      console.log('Started publishing audio');
      return true;

    } catch (error) {
      console.error('Failed to start publishing:', error);
      throw error;
    }
  }

  // Stop publishing audio
  async stopPublishing() {
    if (!this.localParticipant) return;

    try {
      await this.localParticipant.setMicrophoneEnabled(false);
      this.isPublishing = false;

      console.log('Stopped publishing audio');
    } catch (error) {
      console.error('Failed to stop publishing:', error);
    }
  }

  // Send data message to agent
  async sendMessage(text) {
    if (!this.isConnected || !this.room) {
      throw new Error('Not connected to room');
    }

    const encoder = new TextEncoder();
    const data = encoder.encode(JSON.stringify({
      type: 'message',
      text: text,
      timestamp: Date.now()
    }));

    await this.room.localParticipant.publishData(data, { reliable: true });
    console.log('Message sent:', text);
  }

  // Send page context to agent
  async sendPageContext(context) {
    if (!this.isConnected || !this.room) {
      throw new Error('Not connected to room');
    }

    const encoder = new TextEncoder();
    const data = encoder.encode(JSON.stringify({
      type: 'context',
      ...context,
      timestamp: Date.now()
    }));

    await this.room.localParticipant.publishData(data, { reliable: true });
    console.log('Page context sent');
  }

  // Disconnect from room
  async disconnect() {
    if (this.room) {
      await this.room.disconnect();
      this.room = null;
    }

    this.localParticipant = null;
    this.isConnected = false;
    this.isPublishing = false;

    // Remove any attached audio elements
    document.querySelectorAll('#nivora-agent-audio').forEach(el => el.remove());

    console.log('Disconnected from LiveKit');
  }

  // Get audio analyser for visualizations
  getAudioAnalyser() {
    if (!this.localParticipant) return null;

    const tracks = this.localParticipant.audioTracks;
    if (tracks.size === 0) return null;

    const track = tracks.values().next().value?.track;
    if (!track || !track.mediaStreamTrack) return null;

    const audioContext = new AudioContext();
    const mediaStream = new MediaStream([track.mediaStreamTrack]);
    const source = audioContext.createMediaStreamSource(mediaStream);
    const analyser = audioContext.createAnalyser();

    analyser.fftSize = 256;
    source.connect(analyser);

    return analyser;
  }
}

// Export for use in content script
window.NivoraLiveKit = NivoraLiveKit;
