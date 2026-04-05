/**
 * Nivora Voice - LiveKit Integration Module
 *
 * Core module for connecting to LiveKit Cloud and handling
 * real-time voice communication with the Nivora AI agent.
 *
 * Usage:
 *   const voice = new NivoraVoice(config);
 *   await voice.connect();
 *   voice.toggleMic();
 */

// Configuration - Update these values for your deployment
const NIVORA_CONFIG = {
    // LiveKit Cloud WebSocket URL
    livekitUrl: 'wss://nivora-5opea2lo.livekit.cloud',

    // Token server URL (run token-server.py first)
    tokenEndpoint: 'http://localhost:5000/api/livekit-token',

    // Agent configuration
    agentName: 'nivora-agent',

    // Default room prefix (will append unique session ID)
    roomPrefix: 'nivora-session-',

    // Auto-connect on page load (set to false for manual connect)
    autoConnect: false,

    // Reconnection settings
    maxReconnectAttempts: 5,
    reconnectInterval: 2000
};

/**
 * Voice connection states
 */
const VoiceState = {
    DISCONNECTED: 'disconnected',
    CONNECTING: 'connecting',
    CONNECTED: 'connected',
    RECONNECTING: 'reconnecting',
    ERROR: 'error'
};

/**
 * Microphone states
 */
const MicState = {
    MUTED: 'muted',
    UNMUTED: 'unmuted',
    UNAVAILABLE: 'unavailable'
};

/**
 * Agent states
 */
const AgentState = {
    IDLE: 'idle',
    LISTENING: 'listening',
    THINKING: 'thinking',
    SPEAKING: 'speaking'
};

/**
 * Simple event emitter for state changes
 */
class EventEmitter {
    constructor() {
        this.events = {};
    }

    on(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
        return () => this.off(event, callback);
    }

    off(event, callback) {
        if (!this.events[event]) return;
        this.events[event] = this.events[event].filter(cb => cb !== callback);
    }

    emit(event, data) {
        if (!this.events[event]) return;
        this.events[event].forEach(callback => {
            try {
                callback(data);
            } catch (err) {
                console.error(`Error in event handler for ${event}:`, err);
            }
        });
    }
}

/**
 * Main Nivora Voice class
 * Handles LiveKit room connection, audio tracks, and agent communication
 */
class NivoraVoice extends EventEmitter {
    constructor(config = {}) {
        super();

        this.config = { ...NIVORA_CONFIG, ...config };
        this.room = null;
        this.localAudioTrack = null;
        this.remoteAudioElements = [];

        // State
        this.voiceState = VoiceState.DISCONNECTED;
        this.micState = MicState.MUTED;
        this.agentState = AgentState.IDLE;

        // Session info
        this.sessionId = this._generateSessionId();
        this.roomName = this.config.roomPrefix + this.sessionId;

        // Reconnection
        this.reconnectAttempts = 0;
        this.reconnectTimeout = null;

        // Audio context for visualization
        this.audioContext = null;
        this.analyser = null;

        // Bind methods
        this._handleTrackSubscribed = this._handleTrackSubscribed.bind(this);
        this._handleTrackUnsubscribed = this._handleTrackUnsubscribed.bind(this);
        this._handleDisconnected = this._handleDisconnected.bind(this);
        this._handleParticipantConnected = this._handleParticipantConnected.bind(this);
        this._handleActiveSpeakersChanged = this._handleActiveSpeakersChanged.bind(this);
        this._handleConnectionQualityChanged = this._handleConnectionQualityChanged.bind(this);
        this._handleDataReceived = this._handleDataReceived.bind(this);
    }

    /**
     * Generate unique session ID
     */
    _generateSessionId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Update and emit state change
     */
    _setState(type, value) {
        const oldValue = this[type];
        this[type] = value;

        if (oldValue !== value) {
            this.emit('stateChange', { type, oldValue, newValue: value });
            this.emit(type, value);
        }
    }

    /**
     * Fetch access token from backend
     */
    async _getToken() {
        try {
            const response = await fetch(this.config.tokenEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    room: this.roomName,
                    identity: `user-${this.sessionId}`,
                    name: 'User'
                })
            });

            if (!response.ok) {
                throw new Error(`Token request failed: ${response.status}`);
            }

            const data = await response.json();
            return data.token;
        } catch (error) {
            console.error('Failed to get token:', error);
            throw error;
        }
    }

    /**
     * Connect to LiveKit room
     */
    async connect() {
        if (this.voiceState === VoiceState.CONNECTED ||
            this.voiceState === VoiceState.CONNECTING) {
            console.log('Already connected or connecting');
            return;
        }

        this._setState('voiceState', VoiceState.CONNECTING);

        try {
            // Get access token
            const token = await this._getToken();

            // Create room with options
            this.room = new LivekitClient.Room({
                adaptiveStream: true,
                dynacast: true,
                audioCaptureDefaults: {
                    autoGainControl: true,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });

            // Set up event listeners
            this._setupRoomListeners();

            // Connect to room
            await this.room.connect(this.config.livekitUrl, token);

            this._setState('voiceState', VoiceState.CONNECTED);
            this.reconnectAttempts = 0;

            console.log('Connected to room:', this.roomName);
            this.emit('connected', { roomName: this.roomName });

        } catch (error) {
            console.error('Connection failed:', error);
            this._setState('voiceState', VoiceState.ERROR);
            this.emit('error', { type: 'connection', error });

            // Attempt reconnection
            this._scheduleReconnect();
        }
    }

    /**
     * Set up LiveKit room event listeners
     */
    _setupRoomListeners() {
        if (!this.room) return;

        const { RoomEvent } = LivekitClient;

        this.room.on(RoomEvent.TrackSubscribed, this._handleTrackSubscribed);
        this.room.on(RoomEvent.TrackUnsubscribed, this._handleTrackUnsubscribed);
        this.room.on(RoomEvent.Disconnected, this._handleDisconnected);
        this.room.on(RoomEvent.ParticipantConnected, this._handleParticipantConnected);
        this.room.on(RoomEvent.ActiveSpeakersChanged, this._handleActiveSpeakersChanged);
        this.room.on(RoomEvent.ConnectionQualityChanged, this._handleConnectionQualityChanged);
        this.room.on(RoomEvent.DataReceived, this._handleDataReceived);

        // Handle audio playback permission
        this.room.on(RoomEvent.AudioPlaybackStatusChanged, () => {
            if (!this.room.canPlaybackAudio) {
                this.emit('audioPlaybackBlocked', {
                    message: 'Click to enable audio playback'
                });
            }
        });
    }

    /**
     * Handle subscribed track (agent audio)
     */
    _handleTrackSubscribed(track, publication, participant) {
        console.log('Track subscribed:', track.kind, 'from', participant.identity);

        if (track.kind === LivekitClient.Track.Kind.Audio) {
            // Attach audio track to DOM
            const audioElement = track.attach();
            audioElement.id = `audio-${participant.identity}`;
            audioElement.style.display = 'none';
            document.body.appendChild(audioElement);
            this.remoteAudioElements.push(audioElement);

            // Set up audio analyzer for visualization
            this._setupAudioAnalyzer(audioElement);

            this.emit('agentAudioStarted', { participant: participant.identity });
        }
    }

    /**
     * Handle unsubscribed track
     */
    _handleTrackUnsubscribed(track, publication, participant) {
        console.log('Track unsubscribed:', track.kind, 'from', participant.identity);

        if (track.kind === LivekitClient.Track.Kind.Audio) {
            // Remove audio element
            const audioElement = document.getElementById(`audio-${participant.identity}`);
            if (audioElement) {
                audioElement.remove();
                this.remoteAudioElements = this.remoteAudioElements.filter(el => el !== audioElement);
            }

            this.emit('agentAudioStopped', { participant: participant.identity });
        }
    }

    /**
     * Handle disconnection
     */
    _handleDisconnected(reason) {
        console.log('Disconnected:', reason);
        this._setState('voiceState', VoiceState.DISCONNECTED);
        this._setState('micState', MicState.MUTED);
        this._cleanupAudio();

        this.emit('disconnected', { reason });

        // Attempt reconnection if not intentional
        if (reason !== 'CLIENT_INITIATED') {
            this._scheduleReconnect();
        }
    }

    /**
     * Handle participant connected (agent joins)
     */
    _handleParticipantConnected(participant) {
        console.log('Participant connected:', participant.identity);

        if (participant.identity.includes('agent') || participant.identity.includes('nivora')) {
            this._setState('agentState', AgentState.IDLE);
            this.emit('agentConnected', { participant: participant.identity });
        }
    }

    /**
     * Handle active speakers change (for visualization)
     */
    _handleActiveSpeakersChanged(speakers) {
        const agentSpeaking = speakers.some(s =>
            s.identity.includes('agent') || s.identity.includes('nivora')
        );
        const userSpeaking = speakers.some(s =>
            s.identity.includes('user') || s === this.room.localParticipant
        );

        if (agentSpeaking) {
            this._setState('agentState', AgentState.SPEAKING);
        } else if (userSpeaking) {
            this._setState('agentState', AgentState.LISTENING);
        } else {
            this._setState('agentState', AgentState.IDLE);
        }

        this.emit('activeSpeakersChanged', { speakers, agentSpeaking, userSpeaking });
    }

    /**
     * Handle connection quality changes
     */
    _handleConnectionQualityChanged(quality, participant) {
        this.emit('connectionQuality', {
            quality,
            participant: participant.identity,
            isLocal: participant === this.room.localParticipant
        });
    }

    /**
     * Handle data messages (transcriptions, etc.)
     */
    _handleDataReceived(payload, participant, kind) {
        try {
            const decoder = new TextDecoder();
            const data = JSON.parse(decoder.decode(payload));

            this.emit('dataReceived', { data, participant: participant?.identity, kind });

            // Handle specific message types
            if (data.type === 'transcription') {
                this.emit('transcription', {
                    text: data.text,
                    isFinal: data.is_final,
                    speaker: data.speaker
                });
            } else if (data.type === 'agent_state') {
                this._setState('agentState', data.state);
            }
        } catch (e) {
            console.log('Received non-JSON data');
        }
    }

    /**
     * Schedule reconnection attempt
     */
    _scheduleReconnect() {
        if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
            console.log('Max reconnection attempts reached');
            this._setState('voiceState', VoiceState.ERROR);
            this.emit('error', { type: 'maxReconnects', message: 'Max reconnection attempts reached' });
            return;
        }

        this._setState('voiceState', VoiceState.RECONNECTING);
        this.reconnectAttempts++;

        const delay = this.config.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1);
        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

        this.reconnectTimeout = setTimeout(() => {
            this.connect();
        }, delay);
    }

    /**
     * Toggle microphone on/off
     */
    async toggleMic() {
        if (this.voiceState !== VoiceState.CONNECTED) {
            console.log('Cannot toggle mic: not connected');
            return false;
        }

        try {
            const currentState = this.room.localParticipant.isMicrophoneEnabled;
            await this.room.localParticipant.setMicrophoneEnabled(!currentState);

            this._setState('micState', currentState ? MicState.MUTED : MicState.UNMUTED);

            return !currentState;
        } catch (error) {
            console.error('Failed to toggle mic:', error);
            this._setState('micState', MicState.UNAVAILABLE);
            this.emit('error', { type: 'microphone', error });
            return false;
        }
    }

    /**
     * Enable microphone
     */
    async enableMic() {
        if (this.voiceState !== VoiceState.CONNECTED) {
            console.log('Cannot enable mic: not connected');
            return false;
        }

        try {
            await this.room.localParticipant.setMicrophoneEnabled(true);
            this._setState('micState', MicState.UNMUTED);
            return true;
        } catch (error) {
            console.error('Failed to enable mic:', error);
            this._setState('micState', MicState.UNAVAILABLE);
            this.emit('error', { type: 'microphone', error });
            return false;
        }
    }

    /**
     * Disable microphone
     */
    async disableMic() {
        if (this.room) {
            try {
                await this.room.localParticipant.setMicrophoneEnabled(false);
                this._setState('micState', MicState.MUTED);
                return true;
            } catch (error) {
                console.error('Failed to disable mic:', error);
                return false;
            }
        }
        return true;
    }

    /**
     * Enable audio playback (required after user interaction)
     */
    async startAudio() {
        if (this.room) {
            await this.room.startAudio();
        }
    }

    /**
     * Set up audio analyzer for visualization
     */
    _setupAudioAnalyzer(audioElement) {
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }

        try {
            const source = this.audioContext.createMediaElementSource(audioElement);
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;

            source.connect(this.analyser);
            this.analyser.connect(this.audioContext.destination);

            this.emit('analyzerReady', { analyser: this.analyser });
        } catch (e) {
            console.log('Audio analyzer already set up or not available');
        }
    }

    /**
     * Get audio levels for visualization
     */
    getAudioLevels() {
        if (!this.analyser) return { average: 0, peak: 0, frequencies: [] };

        const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
        this.analyser.getByteFrequencyData(dataArray);

        let sum = 0;
        let peak = 0;
        for (let i = 0; i < dataArray.length; i++) {
            sum += dataArray[i];
            if (dataArray[i] > peak) peak = dataArray[i];
        }

        return {
            average: sum / dataArray.length / 255,
            peak: peak / 255,
            frequencies: Array.from(dataArray)
        };
    }

    /**
     * Clean up audio elements
     */
    _cleanupAudio() {
        this.remoteAudioElements.forEach(el => el.remove());
        this.remoteAudioElements = [];

        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
            this.analyser = null;
        }
    }

    /**
     * Disconnect from room
     */
    async disconnect() {
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }

        if (this.room) {
            await this.room.disconnect();
            this.room = null;
        }

        this._cleanupAudio();
        this._setState('voiceState', VoiceState.DISCONNECTED);
        this._setState('micState', MicState.MUTED);
        this._setState('agentState', AgentState.IDLE);
    }

    /**
     * Get current connection status
     */
    getStatus() {
        return {
            voiceState: this.voiceState,
            micState: this.micState,
            agentState: this.agentState,
            roomName: this.roomName,
            sessionId: this.sessionId,
            isConnected: this.voiceState === VoiceState.CONNECTED,
            isMicEnabled: this.micState === MicState.UNMUTED
        };
    }

    /**
     * Send text message to agent
     */
    async sendTextMessage(text) {
        if (!text || !text.trim()) return false;

        if (this.voiceState !== VoiceState.CONNECTED) {
            // Auto-connect if not connected
            await this.connect();
            // Wait a moment for connection
            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        if (!this.room || this.voiceState !== VoiceState.CONNECTED) {
            console.error('Cannot send message: not connected');
            this.emit('error', { type: 'send', message: 'Not connected to room' });
            return false;
        }

        try {
            const message = JSON.stringify({
                type: 'user_message',
                text: text.trim(),
                timestamp: Date.now()
            });

            const encoder = new TextEncoder();
            await this.room.localParticipant.publishData(
                encoder.encode(message),
                { reliable: true }
            );

            // Emit event for UI to show the message
            this.emit('messageSent', { text: text.trim(), speaker: 'user' });
            console.log('Message sent:', text.trim());
            return true;

        } catch (error) {
            console.error('Failed to send message:', error);
            this.emit('error', { type: 'send', error });
            return false;
        }
    }
}

// Export for use
window.NivoraVoice = NivoraVoice;
window.VoiceState = VoiceState;
window.MicState = MicState;
window.AgentState = AgentState;
window.NIVORA_CONFIG = NIVORA_CONFIG;
