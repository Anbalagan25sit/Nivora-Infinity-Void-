/**
 * Nivora Voice UI - State Management and UI Bindings
 *
 * Handles connecting UI elements to the NivoraVoice module,
 * managing visual states, and providing user feedback.
 */

/**
 * Voice UI Controller
 * Binds to DOM elements and manages UI state
 */
class NivoraVoiceUI {
    constructor(voice, options = {}) {
        this.voice = voice;
        this.options = {
            micBtnId: 'mic-btn',
            videoBtnId: 'videocam-btn',
            endBtnId: 'end-session-btn',
            sendBtnId: 'send-btn',
            inputId: 'chat-input',
            messagesId: 'messages-container',
            statusId: 'voice-status',
            orbId: 'orb-container',
            indicatorId: 'voice-indicator',
            ...options
        };

        this.elements = {};
        this.isInitialized = false;

        // Bind methods
        this._onMicClick = this._onMicClick.bind(this);
        this._onEndClick = this._onEndClick.bind(this);
        this._onSendClick = this._onSendClick.bind(this);
        this._onVoiceStateChange = this._onVoiceStateChange.bind(this);
        this._onMicStateChange = this._onMicStateChange.bind(this);
        this._onAgentStateChange = this._onAgentStateChange.bind(this);
        this._onTranscription = this._onTranscription.bind(this);
        this._onError = this._onError.bind(this);
        this._onAudioBlocked = this._onAudioBlocked.bind(this);
    }

    /**
     * Initialize UI bindings
     */
    init() {
        if (this.isInitialized) return;

        // Find and cache DOM elements
        this._findElements();

        // Bind event listeners to DOM
        this._bindDOMEvents();

        // Bind voice events
        this._bindVoiceEvents();

        // Set initial state
        this._updateAllStates();

        this.isInitialized = true;
        console.log('NivoraVoiceUI initialized');
    }

    /**
     * Find and cache DOM elements
     */
    _findElements() {
        const ids = this.options;

        this.elements = {
            micBtn: document.getElementById(ids.micBtnId),
            videoBtn: document.getElementById(ids.videoBtnId),
            endBtn: document.getElementById(ids.endBtnId),
            sendBtn: document.getElementById(ids.sendBtnId),
            input: document.getElementById(ids.inputId),
            messages: document.getElementById(ids.messagesId),
            status: document.getElementById(ids.statusId),
            orb: document.getElementById(ids.orbId),
            indicator: document.getElementById(ids.indicatorId),
            greetingHeader: document.getElementById('greeting-header')
        };

        // Log which elements were found
        Object.entries(this.elements).forEach(([key, el]) => {
            if (el) console.log(`Found element: ${key}`);
        });
    }

    /**
     * Bind DOM event listeners
     */
    _bindDOMEvents() {
        // Mic button
        if (this.elements.micBtn) {
            this.elements.micBtn.addEventListener('click', this._onMicClick);
        }

        // End session button
        if (this.elements.endBtn) {
            this.elements.endBtn.addEventListener('click', this._onEndClick);
        }

        // Send button
        if (this.elements.sendBtn) {
            this.elements.sendBtn.addEventListener('click', this._onSendClick);
        }

        // Enter key to send message
        if (this.elements.input) {
            this.elements.input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this._onSendClick(e);
                }
            });
        }

        // Global click handler for audio playback permission
        document.addEventListener('click', () => {
            if (this.voice.room && !this.voice.room.canPlaybackAudio) {
                this.voice.startAudio();
            }
        }, { once: true });
    }

    /**
     * Bind NivoraVoice events
     */
    _bindVoiceEvents() {
        this.voice.on('voiceState', this._onVoiceStateChange);
        this.voice.on('micState', this._onMicStateChange);
        this.voice.on('agentState', this._onAgentStateChange);
        this.voice.on('transcription', this._onTranscription);
        this.voice.on('error', this._onError);
        this.voice.on('audioPlaybackBlocked', this._onAudioBlocked);

        // Handle sent messages (show in UI)
        this.voice.on('messageSent', ({ text, speaker }) => {
            this._addMessage(text, speaker);
        });

        // Additional events
        this.voice.on('connected', () => {
            this._showNotification('Connected to Nivora', 'success');
        });

        this.voice.on('disconnected', ({ reason }) => {
            if (reason !== 'CLIENT_INITIATED') {
                this._showNotification('Connection lost. Reconnecting...', 'warning');
            }
        });

        this.voice.on('agentConnected', () => {
            this._showNotification('Nivora is ready', 'success');
        });
    }

    /**
     * Handle mic button click
     */
    async _onMicClick(e) {
        e.preventDefault();

        // If not connected, connect first
        if (this.voice.voiceState === VoiceState.DISCONNECTED) {
            await this.voice.connect();
            // Enable mic after connecting
            setTimeout(() => this.voice.enableMic(), 500);
            return;
        }

        // Toggle mic
        await this.voice.toggleMic();
    }

    /**
     * Handle end session button click
     */
    async _onEndClick(e) {
        e.preventDefault();
        await this.voice.disconnect();
        this._showNotification('Session ended', 'info');
    }

    /**
     * Handle send button click
     */
    async _onSendClick(e) {
        e.preventDefault();

        if (this.elements.input) {
            const text = this.elements.input.value.trim();
            if (text) {
                // Send message via voice module
                const sent = await this.voice.sendTextMessage(text);
                if (sent) {
                    this.elements.input.value = '';
                }
            }
        }
    }

    /**
     * Handle voice state changes
     */
    _onVoiceStateChange(state) {
        this._updateConnectionUI(state);

        // Update body class for global styling
        document.body.classList.remove(
            'voice-disconnected',
            'voice-connecting',
            'voice-connected',
            'voice-reconnecting',
            'voice-error'
        );
        document.body.classList.add(`voice-${state}`);
    }

    /**
     * Handle mic state changes
     */
    _onMicStateChange(state) {
        this._updateMicUI(state);
    }

    /**
     * Handle agent state changes
     */
    _onAgentStateChange(state) {
        this._updateAgentUI(state);

        // Update orb animation
        if (this.elements.orb) {
            this.elements.orb.classList.remove(
                'agent-idle',
                'agent-listening',
                'agent-thinking',
                'agent-speaking'
            );
            this.elements.orb.classList.add(`agent-${state}`);
        }
    }

    /**
     * Handle transcription events
     */
    _onTranscription({ text, isFinal, speaker }) {
        // Update input field with transcription
        if (this.elements.input && speaker === 'user') {
            if (isFinal) {
                this.elements.input.value = text;
            } else {
                this.elements.input.value = text + '...';
            }
        }

        // Add message to chat if final
        if (isFinal && this.elements.messages) {
            this._addMessage(text, speaker);
        }
    }

    /**
     * Handle errors
     */
    _onError({ type, error, message }) {
        console.error('Voice error:', type, error || message);

        let errorMsg = 'An error occurred';

        switch (type) {
            case 'connection':
                errorMsg = 'Failed to connect. Please try again.';
                break;
            case 'microphone':
                errorMsg = 'Microphone access denied. Please allow microphone access.';
                break;
            case 'maxReconnects':
                errorMsg = 'Unable to reconnect. Please refresh the page.';
                break;
            default:
                errorMsg = message || 'An unexpected error occurred.';
        }

        this._showNotification(errorMsg, 'error');
    }

    /**
     * Handle audio playback blocked
     */
    _onAudioBlocked({ message }) {
        this._showNotification('Click anywhere to enable audio', 'warning');
    }

    /**
     * Update connection UI state
     */
    _updateConnectionUI(state) {
        const statusText = {
            [VoiceState.DISCONNECTED]: 'Not connected',
            [VoiceState.CONNECTING]: 'Connecting...',
            [VoiceState.CONNECTED]: 'Connected',
            [VoiceState.RECONNECTING]: 'Reconnecting...',
            [VoiceState.ERROR]: 'Connection error'
        };

        // Update status element
        if (this.elements.status) {
            this.elements.status.textContent = statusText[state] || state;
            this.elements.status.className = `voice-status voice-status-${state}`;
        }

        // Update indicator
        if (this.elements.indicator) {
            this.elements.indicator.classList.remove('indicator-connected', 'indicator-connecting', 'indicator-error');

            if (state === VoiceState.CONNECTED) {
                this.elements.indicator.classList.add('indicator-connected');
            } else if (state === VoiceState.CONNECTING || state === VoiceState.RECONNECTING) {
                this.elements.indicator.classList.add('indicator-connecting');
            } else if (state === VoiceState.ERROR) {
                this.elements.indicator.classList.add('indicator-error');
            }
        }

        // Update end button state
        if (this.elements.endBtn) {
            this.elements.endBtn.disabled = state === VoiceState.DISCONNECTED;
        }
    }

    /**
     * Update microphone UI state
     */
    _updateMicUI(state) {
        if (!this.elements.micBtn) return;

        const micIcon = this.elements.micBtn.querySelector('.material-symbols-outlined');

        this.elements.micBtn.classList.remove('mic-muted', 'mic-unmuted', 'mic-unavailable');
        this.elements.micBtn.classList.add(`mic-${state}`);

        // Update icon
        if (micIcon) {
            if (state === MicState.MUTED) {
                micIcon.textContent = 'mic_off';
                micIcon.style.fontVariationSettings = "'FILL' 0";
            } else if (state === MicState.UNMUTED) {
                micIcon.textContent = 'mic';
                micIcon.style.fontVariationSettings = "'FILL' 1";
            } else {
                micIcon.textContent = 'mic_off';
            }
        }

        // Update button style
        if (state === MicState.UNMUTED) {
            this.elements.micBtn.classList.add('bg-primary', 'text-on-primary');
            this.elements.micBtn.classList.remove('text-on-surface');
        } else {
            this.elements.micBtn.classList.remove('bg-primary', 'text-on-primary');
            this.elements.micBtn.classList.add('text-on-surface');
        }
    }

    /**
     * Update agent state UI
     */
    _updateAgentUI(state) {
        // This is handled by CSS classes on the orb
        // Additional UI updates can be added here

        // Update indicator text if present
        const modeIndicator = document.querySelector('[data-agent-state]');
        if (modeIndicator) {
            const stateText = {
                [AgentState.IDLE]: 'Ready',
                [AgentState.LISTENING]: 'Listening...',
                [AgentState.THINKING]: 'Thinking...',
                [AgentState.SPEAKING]: 'Speaking...'
            };
            modeIndicator.textContent = stateText[state] || state;
        }
    }

    /**
     * Add message to chat container
     */
    _addMessage(text, speaker) {
        if (!this.elements.messages) return;

        // Show messages container and hide greeting
        this.elements.messages.classList.remove('hidden');
        if (this.elements.greetingHeader) {
            this.elements.greetingHeader.classList.add('hidden');
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${speaker}`;

        const isUser = speaker === 'user';
        messageDiv.innerHTML = `
            <div class="flex ${isUser ? 'justify-end' : 'justify-start'}">
                <div class="${isUser ? 'bg-surface-container-low' : 'bg-surface-container-lowest border-l-2 border-primary/30'} px-4 py-3 rounded-2xl max-w-[80%]">
                    ${!isUser ? '<div class="flex items-center gap-2 mb-2"><span class="material-symbols-outlined text-primary text-sm" style="font-variation-settings: \'FILL\' 1;">auto_awesome</span><span class="text-[10px] text-primary uppercase tracking-widest font-semibold">Nivora</span></div>' : ''}
                    <p class="text-sm text-on-surface leading-relaxed">${this._escapeHtml(text)}</p>
                </div>
            </div>
        `;

        this.elements.messages.appendChild(messageDiv);
        this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
    }

    /**
     * Show notification toast
     */
    _showNotification(message, type = 'info') {
        // Remove existing notification
        const existing = document.querySelector('.voice-notification');
        if (existing) existing.remove();

        const notification = document.createElement('div');
        notification.className = `voice-notification voice-notification-${type}`;
        notification.innerHTML = `
            <div class="flex items-center gap-2 px-4 py-3 rounded-lg shadow-lg bg-surface-container border border-outline-variant/20">
                <span class="material-symbols-outlined text-sm">${this._getNotificationIcon(type)}</span>
                <span class="text-sm">${message}</span>
            </div>
        `;

        // Position at bottom center
        notification.style.cssText = `
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
            animation: slideUp 0.3s ease-out;
        `;

        document.body.appendChild(notification);

        // Auto-remove after 4 seconds
        setTimeout(() => {
            notification.style.animation = 'slideDown 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }

    /**
     * Get notification icon based on type
     */
    _getNotificationIcon(type) {
        const icons = {
            success: 'check_circle',
            error: 'error',
            warning: 'warning',
            info: 'info'
        };
        return icons[type] || icons.info;
    }

    /**
     * Escape HTML to prevent XSS
     */
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Update all UI states
     */
    _updateAllStates() {
        this._updateConnectionUI(this.voice.voiceState);
        this._updateMicUI(this.voice.micState);
        this._updateAgentUI(this.voice.agentState);
    }

    /**
     * Cleanup
     */
    destroy() {
        // Remove event listeners
        if (this.elements.micBtn) {
            this.elements.micBtn.removeEventListener('click', this._onMicClick);
        }
        if (this.elements.endBtn) {
            this.elements.endBtn.removeEventListener('click', this._onEndClick);
        }
        if (this.elements.sendBtn) {
            this.elements.sendBtn.removeEventListener('click', this._onSendClick);
        }

        // Remove body classes
        document.body.classList.remove(
            'voice-disconnected',
            'voice-connecting',
            'voice-connected',
            'voice-reconnecting',
            'voice-error'
        );

        this.isInitialized = false;
    }
}

/**
 * Auto-initialize on DOM ready
 */
function initNivoraVoiceUI() {
    // Check if LiveKit SDK is loaded
    if (typeof LivekitClient === 'undefined') {
        console.error('LiveKit Client SDK not loaded. Include it before voice-ui.js');
        return;
    }

    // Check if NivoraVoice is available
    if (typeof NivoraVoice === 'undefined') {
        console.error('NivoraVoice not loaded. Include nivora-voice.js before voice-ui.js');
        return;
    }

    // Create voice instance
    const voice = new NivoraVoice();

    // Create UI controller
    const ui = new NivoraVoiceUI(voice);

    // Initialize
    ui.init();

    // Expose globally for debugging
    window.nivoraVoice = voice;
    window.nivoraUI = ui;

    console.log('Nivora Voice UI ready. Access via window.nivoraVoice and window.nivoraUI');
}

// Export
window.NivoraVoiceUI = NivoraVoiceUI;
window.initNivoraVoiceUI = initNivoraVoiceUI;

// Auto-init when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNivoraVoiceUI);
} else {
    initNivoraVoiceUI();
}
