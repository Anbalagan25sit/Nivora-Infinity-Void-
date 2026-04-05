/**
 * Nivora Chat - Text-to-Text Chat Module
 *
 * Handles text-based chat with Nivora AI via the backend API.
 * Supports both regular and streaming responses.
 *
 * Usage:
 *   const chat = new NivoraChat();
 *   const response = await chat.sendMessage("Hello!");
 *   // or with streaming:
 *   chat.sendMessageStream("Hello!", (text) => console.log(text));
 */

// Configuration
const NIVORA_CHAT_CONFIG = {
    // Chat API endpoint (token-server.py)
    apiEndpoint: 'http://localhost:5000/api/chat',
    streamEndpoint: 'http://localhost:5000/api/chat/stream',
    clearEndpoint: 'http://localhost:5000/api/chat/clear',

    // Enable streaming responses (smoother UX)
    useStreaming: true,

    // Session persistence
    persistSession: true
};

/**
 * Chat states
 */
const ChatState = {
    IDLE: 'idle',
    SENDING: 'sending',
    RECEIVING: 'receiving',
    ERROR: 'error'
};

/**
 * Simple event emitter
 */
class ChatEventEmitter {
    constructor() {
        this.events = {};
    }

    on(event, callback) {
        if (!this.events[event]) this.events[event] = [];
        this.events[event].push(callback);
        return () => this.off(event, callback);
    }

    off(event, callback) {
        if (!this.events[event]) return;
        this.events[event] = this.events[event].filter(cb => cb !== callback);
    }

    emit(event, data) {
        if (!this.events[event]) return;
        this.events[event].forEach(cb => {
            try { cb(data); }
            catch (e) { console.error(`Error in ${event} handler:`, e); }
        });
    }
}

/**
 * Main Nivora Chat class
 */
class NivoraChat extends ChatEventEmitter {
    constructor(config = {}) {
        super();
        this.config = { ...NIVORA_CHAT_CONFIG, ...config };
        this.state = ChatState.IDLE;
        this.sessionId = this._loadOrCreateSession();
        this.messages = [];
        this.abortController = null;
    }

    /**
     * Load or create session ID
     */
    _loadOrCreateSession() {
        if (this.config.persistSession) {
            const stored = localStorage.getItem('nivora_session_id');
            if (stored) return stored;
        }
        const newId = 'session_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
        if (this.config.persistSession) {
            localStorage.setItem('nivora_session_id', newId);
        }
        return newId;
    }

    /**
     * Update state and emit event
     */
    _setState(newState) {
        const oldState = this.state;
        this.state = newState;
        if (oldState !== newState) {
            this.emit('stateChange', { oldState, newState });
        }
    }

    /**
     * Send a message and get a response (non-streaming)
     * @param {string} message - User message
     * @returns {Promise<string>} - AI response
     */
    async sendMessage(message) {
        if (!message || !message.trim()) {
            throw new Error('Empty message');
        }

        if (this.state === ChatState.SENDING || this.state === ChatState.RECEIVING) {
            throw new Error('Already processing a message');
        }

        this._setState(ChatState.SENDING);

        // Add to local history
        this.messages.push({ role: 'user', text: message, timestamp: Date.now() });

        try {
            const response = await fetch(this.config.apiEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message.trim(),
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || `HTTP ${response.status}`);
            }

            const data = await response.json();

            // Update session ID if returned
            if (data.session_id) {
                this.sessionId = data.session_id;
                if (this.config.persistSession) {
                    localStorage.setItem('nivora_session_id', this.sessionId);
                }
            }

            // Add to local history
            this.messages.push({ role: 'assistant', text: data.reply, timestamp: Date.now() });

            this._setState(ChatState.IDLE);

            return data.reply;

        } catch (error) {
            console.error('Chat error:', error);
            this._setState(ChatState.ERROR);
            this.emit('error', { message: error.message, type: 'send' });
            throw error;
        }
    }

    /**
     * Send a message with streaming response
     * @param {string} message - User message
     * @param {function} onChunk - Callback for each text chunk
     * @returns {Promise<string>} - Complete response
     */
    async sendMessageStream(message, onChunk = null) {
        if (!message || !message.trim()) {
            throw new Error('Empty message');
        }

        if (this.state === ChatState.SENDING || this.state === ChatState.RECEIVING) {
            throw new Error('Already processing a message');
        }

        this._setState(ChatState.SENDING);
        this.emit('messageSent', { text: message, speaker: 'user' });

        // Add to local history
        this.messages.push({ role: 'user', text: message, timestamp: Date.now() });

        // Create abort controller for cancellation
        this.abortController = new AbortController();

        try {
            const response = await fetch(this.config.streamEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message.trim(),
                    session_id: this.sessionId
                }),
                signal: this.abortController.signal
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || `HTTP ${response.status}`);
            }

            this._setState(ChatState.RECEIVING);
            this.emit('streamStart', {});

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullResponse = '';
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });

                // Process SSE data
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));

                            if (data.text && !data.done) {
                                fullResponse += data.text;
                                if (onChunk) onChunk(data.text);
                                this.emit('streamChunk', { text: data.text, fullText: fullResponse });
                            }

                            if (data.done) {
                                if (data.session_id) {
                                    this.sessionId = data.session_id;
                                    if (this.config.persistSession) {
                                        localStorage.setItem('nivora_session_id', this.sessionId);
                                    }
                                }
                            }
                        } catch (e) {
                            // Ignore parse errors for incomplete chunks
                        }
                    }
                }
            }

            // Add to local history (only once at the end)
            this.messages.push({ role: 'assistant', text: fullResponse, timestamp: Date.now() });

            this._setState(ChatState.IDLE);
            this.emit('streamEnd', { fullText: fullResponse });
            // Don't emit messageReceived for streaming - we already showed the message via streamChunk

            return fullResponse;

        } catch (error) {
            if (error.name === 'AbortError') {
                console.log('Stream cancelled');
                this._setState(ChatState.IDLE);
                return '';
            }

            console.error('Stream error:', error);
            this._setState(ChatState.ERROR);
            this.emit('error', { message: error.message, type: 'stream' });
            throw error;

        } finally {
            this.abortController = null;
        }
    }

    /**
     * Cancel current streaming response
     */
    cancelStream() {
        if (this.abortController) {
            this.abortController.abort();
            this.abortController = null;
        }
    }

    /**
     * Clear chat history (local and server)
     */
    async clearHistory() {
        try {
            await fetch(this.config.clearEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: this.sessionId })
            });
        } catch (e) {
            console.warn('Failed to clear server history:', e);
        }

        // Clear local
        this.messages = [];
        this.sessionId = this._loadOrCreateSession();
        this.emit('historyCleared', {});
    }

    /**
     * Get current state
     */
    getState() {
        return {
            state: this.state,
            sessionId: this.sessionId,
            messageCount: this.messages.length,
            isProcessing: this.state === ChatState.SENDING || this.state === ChatState.RECEIVING
        };
    }

    /**
     * Get chat history
     */
    getHistory() {
        return [...this.messages];
    }
}

/**
 * Nivora Chat UI Controller
 * Binds NivoraChat to DOM elements
 */
class NivoraChatUI {
    constructor(chat, options = {}) {
        this.chat = chat;
        this.options = {
            inputId: 'chat-input',
            sendBtnId: 'send-btn',
            messagesId: 'messages-container',
            greetingId: 'greeting-header',
            quickActionsId: 'quick-actions',
            inputContainerId: 'chat-input-container',
            chatWrapperId: 'chat-wrapper',
            typingIndicatorClass: 'typing-indicator',
            useStreaming: false,
            ...options
        };

        this.elements = {};
        this.hasStartedChat = false;

        // Bind methods
        this._onSendClick = this._onSendClick.bind(this);
        this._onKeyDown = this._onKeyDown.bind(this);
    }

    /**
     * Initialize UI bindings
     */
    init() {
        // Find elements
        this.elements = {
            input: document.getElementById(this.options.inputId),
            sendBtn: document.getElementById(this.options.sendBtnId),
            messages: document.getElementById(this.options.messagesId),
            greeting: document.getElementById(this.options.greetingId),
            quickActions: document.getElementById(this.options.quickActionsId),
            inputContainer: document.getElementById(this.options.inputContainerId),
            chatWrapper: document.getElementById(this.options.chatWrapperId)
        };

        // Bind DOM events
        if (this.elements.sendBtn) {
            this.elements.sendBtn.addEventListener('click', this._onSendClick);
        }

        if (this.elements.input) {
            this.elements.input.addEventListener('keydown', this._onKeyDown);
        }

        // Bind chat events
        this.chat.on('stateChange', ({ newState }) => this._updateButtonState(newState));
        this.chat.on('error', ({ message }) => this._showError(message));

        console.log('NivoraChatUI initialized');
    }

    /**
     * Handle send button click
     */
    async _onSendClick(e) {
        e?.preventDefault();

        const input = this.elements.input;
        if (!input) return;

        const text = input.value.trim();
        if (!text) return;

        // Check if already processing
        if (this.chat.state === ChatState.SENDING || this.chat.state === ChatState.RECEIVING) {
            return;
        }

        // Clear input immediately
        input.value = '';
        input.style.height = 'auto';

        // Transform to chat mode on first message
        if (!this.hasStartedChat) {
            this._transformToChatMode();
        }

        // Hide greeting
        if (this.elements.greeting) {
            this.elements.greeting.classList.add('hidden');
        }

        // Show messages container
        if (this.elements.messages) {
            this.elements.messages.classList.remove('hidden');
        }

        // Add user message to UI
        this._addMessage(text, 'user');

        // Show thinking indicator with Nivora logo
        this._showThinkingIndicator();

        try {
            // Send message and get response from AWS Bedrock
            const response = await this.chat.sendMessage(text);

            // Remove thinking indicator and show response
            this._hideThinkingIndicator();
            this._addMessage(response, 'agent');

        } catch (error) {
            this._hideThinkingIndicator();
            this._showError(error.message || 'Failed to get response');
        }
    }

    /**
     * Transform UI to chat mode (compact input, hide greeting/quick actions)
     */
    _transformToChatMode() {
        this.hasStartedChat = true;

        // Add chat-started class to body for CSS targeting
        document.body.classList.add('chat-started');

        // Make input compact
        if (this.elements.inputContainer) {
            this.elements.inputContainer.classList.add('input-compact');
        }

        // Hide quick actions
        if (this.elements.quickActions) {
            this.elements.quickActions.style.display = 'none';
        }

        // Change chat wrapper layout
        if (this.elements.chatWrapper) {
            this.elements.chatWrapper.classList.remove('chat-centered');
            this.elements.chatWrapper.classList.add('chat-active');
        }

        // Update placeholder
        if (this.elements.input) {
            this.elements.input.placeholder = 'Message Nivora...';
        }
    }

    /**
     * Handle Enter key
     */
    _onKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this._onSendClick();
        }
    }

    /**
     * Add message to chat
     */
    _addMessage(text, speaker) {
        if (!this.elements.messages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${speaker} animate-fadeIn`;

        const isUser = speaker === 'user';

        if (isUser) {
            // User message - simple text
            messageDiv.innerHTML = `
                <div class="flex justify-end mb-4">
                    <div class="bg-surface-container-high px-4 py-3 rounded-2xl max-w-[80%]">
                        <p class="text-sm text-on-surface leading-relaxed whitespace-pre-wrap">${this._escapeHtml(text)}</p>
                    </div>
                </div>
            `;
        } else {
            // Agent message - with Nivora branding and markdown rendering
            const renderedContent = this._renderMarkdown(text);
            messageDiv.innerHTML = `
                <div class="flex justify-start mb-6">
                    <div class="flex gap-3 max-w-[90%]">
                        <!-- Nivora Avatar -->
                        <div class="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-primary/20 to-primary-container/30 flex items-center justify-center border border-primary/20 p-1">
                            <img src="assets/nivora-logo.png" alt="Nivora" class="w-full h-full object-contain"/>
                        </div>
                        <!-- Message Content -->
                        <div class="flex-1 min-w-0">
                            <div class="text-[11px] text-primary/70 font-semibold uppercase tracking-wider mb-2">Nivora</div>
                            <div class="markdown-body">${renderedContent}</div>
                        </div>
                    </div>
                </div>
            `;
        }

        this.elements.messages.appendChild(messageDiv);
        this._scrollToBottom();
    }

    /**
     * Render markdown to HTML (Claude-style)
     */
    _renderMarkdown(text) {
        if (typeof marked !== 'undefined') {
            try {
                return marked.parse(text);
            } catch (e) {
                console.warn('Markdown parsing failed:', e);
            }
        }
        // Fallback: basic formatting
        return this._escapeHtml(text)
            .replace(/\n/g, '<br>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/\*([^*]+)\*/g, '<em>$1</em>');
    }

    /**
     * Show thinking indicator with Nivora logo and spinning ring with nodes
     */
    _showThinkingIndicator() {
        if (!this.elements.messages) return;

        const indicator = document.createElement('div');
        indicator.className = `${this.options.typingIndicatorClass} flex justify-start mb-6 animate-fadeIn`;
        indicator.innerHTML = `
            <div class="flex gap-4 items-start">
                <!-- Nivora Avatar with Spinning Ring & Nodes -->
                <div class="flex-shrink-0 relative w-12 h-12">
                    <!-- Spinning ring with nodes (like ship wheel) -->
                    <svg class="w-12 h-12 thinking-ring absolute inset-0" viewBox="0 0 48 48">
                        <!-- Outer ring -->
                        <circle cx="24" cy="24" r="20" fill="none" stroke="#434653" stroke-width="2" opacity="0.3"/>
                        <!-- Spokes -->
                        <line x1="24" y1="4" x2="24" y2="14" stroke="#b1c5ff" stroke-width="2" stroke-linecap="round"/>
                        <line x1="24" y1="34" x2="24" y2="44" stroke="#b1c5ff" stroke-width="2" stroke-linecap="round"/>
                        <line x1="4" y1="24" x2="14" y2="24" stroke="#b1c5ff" stroke-width="2" stroke-linecap="round"/>
                        <line x1="34" y1="24" x2="44" y2="24" stroke="#b1c5ff" stroke-width="2" stroke-linecap="round"/>
                        <line x1="9.86" y1="9.86" x2="16.93" y2="16.93" stroke="#b1c5ff" stroke-width="2" stroke-linecap="round"/>
                        <line x1="31.07" y1="31.07" x2="38.14" y2="38.14" stroke="#b1c5ff" stroke-width="2" stroke-linecap="round"/>
                        <line x1="9.86" y1="38.14" x2="16.93" y2="31.07" stroke="#b1c5ff" stroke-width="2" stroke-linecap="round"/>
                        <line x1="31.07" y1="16.93" x2="38.14" y2="9.86" stroke="#b1c5ff" stroke-width="2" stroke-linecap="round"/>
                        <!-- Nodes at the ends -->
                        <circle cx="24" cy="4" r="3" fill="#b1c5ff"/>
                        <circle cx="24" cy="44" r="3" fill="#b1c5ff"/>
                        <circle cx="4" cy="24" r="3" fill="#b1c5ff"/>
                        <circle cx="44" cy="24" r="3" fill="#b1c5ff"/>
                        <circle cx="9.86" cy="9.86" r="3" fill="#b1c5ff" opacity="0.7"/>
                        <circle cx="38.14" cy="38.14" r="3" fill="#b1c5ff" opacity="0.7"/>
                        <circle cx="9.86" cy="38.14" r="3" fill="#b1c5ff" opacity="0.7"/>
                        <circle cx="38.14" cy="9.86" r="3" fill="#b1c5ff" opacity="0.7"/>
                    </svg>
                    <!-- Center Nivora icon -->
                    <div class="absolute inset-0 flex items-center justify-center">
                        <div class="w-6 h-6 rounded-full bg-surface-container flex items-center justify-center p-1">
                            <img src="assets/nivora-logo.png" alt="Nivora" class="w-full h-full object-contain"/>
                        </div>
                    </div>
                </div>
                <!-- Thinking text -->
                <div class="flex flex-col justify-center pt-1">
                    <div class="text-[11px] text-primary/70 font-semibold uppercase tracking-wider mb-1">Nivora</div>
                    <div class="text-sm text-on-surface-variant">Thinking<span class="thinking-dots"></span></div>
                </div>
            </div>
        `;

        this.elements.messages.appendChild(indicator);
        this._scrollToBottom();
    }

    /**
     * Hide thinking indicator
     */
    _hideThinkingIndicator() {
        const indicator = document.querySelector(`.${this.options.typingIndicatorClass}`);
        if (indicator) indicator.remove();
    }

    /**
     * Show error message
     */
    _showError(message) {
        this._hideThinkingIndicator();

        if (!this.elements.messages) return;

        const errorDiv = document.createElement('div');
        errorDiv.className = 'message message-error flex justify-start mb-4 animate-fadeIn';
        errorDiv.innerHTML = `
            <div class="flex gap-3">
                <div class="flex-shrink-0 w-8 h-8 rounded-full bg-error/20 flex items-center justify-center">
                    <span class="material-symbols-outlined text-error text-[16px]">error</span>
                </div>
                <div class="bg-error-container/10 border border-error/20 px-4 py-3 rounded-2xl">
                    <div class="text-sm text-error">${this._escapeHtml(message)}</div>
                    <button onclick="this.parentElement.parentElement.parentElement.remove()" class="text-xs text-error/60 hover:text-error mt-2">Dismiss</button>
                </div>
            </div>
        `;

        this.elements.messages.appendChild(errorDiv);
        this._scrollToBottom();
    }

    /**
     * Update send button state
     */
    _updateButtonState(state) {
        if (!this.elements.sendBtn) return;

        const icon = this.elements.sendBtn.querySelector('.material-symbols-outlined');
        const isProcessing = state === ChatState.SENDING || state === ChatState.RECEIVING;

        this.elements.sendBtn.disabled = isProcessing;
        this.elements.sendBtn.style.opacity = isProcessing ? '0.5' : '1';

        if (icon) {
            icon.textContent = isProcessing ? 'hourglass_empty' : 'arrow_upward';
        }
    }

    /**
     * Scroll messages to bottom
     */
    _scrollToBottom() {
        if (this.elements.messages) {
            setTimeout(() => {
                this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
            }, 50);
        }
    }

    /**
     * Escape HTML
     */
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Cleanup
     */
    destroy() {
        if (this.elements.sendBtn) {
            this.elements.sendBtn.removeEventListener('click', this._onSendClick);
        }
        if (this.elements.input) {
            this.elements.input.removeEventListener('keydown', this._onKeyDown);
        }
    }
}

/**
 * Auto-initialize on DOM ready
 */
function initNivoraChat() {
    // Create chat instance
    const chat = new NivoraChat();

    // Create UI controller - use NON-streaming for cleaner responses
    const ui = new NivoraChatUI(chat, {
        useStreaming: false  // Disable streaming to prevent duplicate responses
    });

    // Initialize
    ui.init();

    // Expose globally for debugging
    window.nivoraChat = chat;
    window.nivoraChatUI = ui;

    console.log('Nivora Chat ready. Access via window.nivoraChat and window.nivoraChatUI');
}

// Export
window.NivoraChat = NivoraChat;
window.NivoraChatUI = NivoraChatUI;
window.ChatState = ChatState;
window.initNivoraChat = initNivoraChat;

// Auto-init when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNivoraChat);
} else {
    initNivoraChat();
}
