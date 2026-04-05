/**
 * Nivora Chat - ENHANCED with Tool Support & Animations
 *
 * Handles text-based chat with Nivora AI via the backend API WITH TOOLS.
 * Features beautiful animations when tools are called.
 */

// Configuration
const NIVORA_CHAT_CONFIG = {
    // Chat API endpoint (token-server-enhanced.py)
    apiEndpoint: 'http://localhost:5000/api/chat',
    clearEndpoint: 'http://localhost:5000/api/chat/clear',

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
    USING_TOOL: 'using_tool',
    ERROR: 'error'
};

/**
 * Tool icons and colors - ALL TOOLS from agent.py
 */
const TOOL_METADATA = {
    // ═══════════════════════════════════════════════════════════════════
    // BASIC TOOLS (No credentials needed)
    // ═══════════════════════════════════════════════════════════════════
    open_website: {
        icon: 'language',
        color: '#b1c5ff',
        label: 'Opening website'
    },
    web_search: {
        icon: 'search',
        color: '#b1c5ff',
        label: 'Searching the web'
    },
    get_weather: {
        icon: 'wb_sunny',
        color: '#ffb59e',
        label: 'Getting weather'
    },
    system_control: {
        icon: 'settings_remote',
        color: '#8b5cf6',
        label: 'System control'
    },

    // ═══════════════════════════════════════════════════════════════════
    // UNIVERSAL MEDIA CONTROLS
    // ═══════════════════════════════════════════════════════════════════
    pause_media: {
        icon: 'pause_circle',
        color: '#f59e0b',
        label: 'Pausing media'
    },
    next_track: {
        icon: 'skip_next',
        color: '#f59e0b',
        label: 'Next track'
    },
    previous_track: {
        icon: 'skip_previous',
        color: '#f59e0b',
        label: 'Previous track'
    },
    volume_control: {
        icon: 'volume_up',
        color: '#f59e0b',
        label: 'Adjusting volume'
    },

    // ═══════════════════════════════════════════════════════════════════
    // NOTES & REMINDERS
    // ═══════════════════════════════════════════════════════════════════
    take_note: {
        icon: 'note_add',
        color: '#fbbf24',
        label: 'Taking note'
    },
    read_notes: {
        icon: 'sticky_note_2',
        color: '#fbbf24',
        label: 'Reading notes'
    },
    set_reminder: {
        icon: 'alarm',
        color: '#fb923c',
        label: 'Setting reminder'
    },

    // ═══════════════════════════════════════════════════════════════════
    // SCREEN SHARE VISION
    // ═══════════════════════════════════════════════════════════════════
    describe_screen_share: {
        icon: 'screen_share',
        color: '#ec4899',
        label: 'Analyzing screen'
    },

    // ═══════════════════════════════════════════════════════════════════
    // EMAIL TOOLS (Gmail)
    // ═══════════════════════════════════════════════════════════════════
    send_email: {
        icon: 'mail',
        color: '#4ade80',
        label: 'Sending email'
    },
    read_emails: {
        icon: 'inbox',
        color: '#60a5fa',
        label: 'Reading emails'
    },

    // ═══════════════════════════════════════════════════════════════════
    // GOOGLE APPS
    // ═══════════════════════════════════════════════════════════════════
    google_sheets_read: {
        icon: 'table_chart',
        color: '#34a853',
        label: 'Reading Google Sheet'
    },
    google_sheets_write: {
        icon: 'edit_note',
        color: '#34a853',
        label: 'Writing to Google Sheet'
    },
    google_calendar_list: {
        icon: 'calendar_month',
        color: '#4285f4',
        label: 'Checking calendar'
    },

    // ═══════════════════════════════════════════════════════════════════
    // SPOTIFY API TOOLS
    // ═══════════════════════════════════════════════════════════════════
    spotify_play: {
        icon: 'play_circle',
        color: '#1db954',
        label: 'Playing on Spotify'
    },
    spotify_control: {
        icon: 'tune',
        color: '#1db954',
        label: 'Controlling Spotify'
    },
    spotify_shortcut: {
        icon: 'keyboard',
        color: '#1db954',
        label: 'Spotify shortcut'
    },
    spotify_search: {
        icon: 'search',
        color: '#1db954',
        label: 'Searching Spotify'
    },
    spotify_get_track_info: {
        icon: 'music_note',
        color: '#1db954',
        label: 'Getting track info'
    },
    spotify_get_artist_info: {
        icon: 'person',
        color: '#1db954',
        label: 'Getting artist info'
    },
    spotify_get_artist_top_tracks: {
        icon: 'trending_up',
        color: '#1db954',
        label: 'Getting top tracks'
    },
    spotify_get_recommendations: {
        icon: 'recommend',
        color: '#1db954',
        label: 'Getting recommendations'
    },
    spotify_get_playlist: {
        icon: 'queue_music',
        color: '#1db954',
        label: 'Getting playlist'
    },
    spotify_get_featured_playlists: {
        icon: 'featured_play_list',
        color: '#1db954',
        label: 'Getting featured playlists'
    },
    spotify_get_new_releases: {
        icon: 'new_releases',
        color: '#1db954',
        label: 'Getting new releases'
    },
    spotify_get_categories: {
        icon: 'category',
        color: '#1db954',
        label: 'Getting categories'
    },
    spotify_get_category_playlists: {
        icon: 'playlist_play',
        color: '#1db954',
        label: 'Getting category playlists'
    },
    spotify_get_available_genres: {
        icon: 'library_music',
        color: '#1db954',
        label: 'Getting genres'
    },
    open_spotify: {
        icon: 'open_in_new',
        color: '#1db954',
        label: 'Opening Spotify'
    },

    // ═══════════════════════════════════════════════════════════════════
    // LOCAL SPOTIFY CONTROL (No API needed)
    // ═══════════════════════════════════════════════════════════════════
    spotify_play_media: {
        icon: 'play_arrow',
        color: '#1db954',
        label: 'Playing media'
    },
    spotify_control_playback: {
        icon: 'settings_remote',
        color: '#1db954',
        label: 'Controlling playback'
    },
    spotify_what_is_playing: {
        icon: 'radio',
        color: '#1db954',
        label: 'Checking now playing'
    },
    spotify_mute_application: {
        icon: 'volume_off',
        color: '#1db954',
        label: 'Muting Spotify'
    },
    spotify_toggle_shuffle: {
        icon: 'shuffle',
        color: '#1db954',
        label: 'Toggling shuffle'
    },
    spotify_cycle_repeat: {
        icon: 'repeat',
        color: '#1db954',
        label: 'Cycling repeat'
    },
    spotify_volume: {
        icon: 'volume_up',
        color: '#1db954',
        label: 'Adjusting Spotify volume'
    },

    // ═══════════════════════════════════════════════════════════════════
    // ADVANCED SPOTIFY TOOLS (from spotify_tools_advanced.py)
    // ═══════════════════════════════════════════════════════════════════
    spotify_play_track: {
        icon: 'music_note',
        color: '#1db954',
        label: 'Playing track'
    },
    spotify_play_album: {
        icon: 'album',
        color: '#1db954',
        label: 'Playing album'
    },
    spotify_play_artist: {
        icon: 'person',
        color: '#1db954',
        label: 'Playing artist'
    },
    spotify_play_playlist: {
        icon: 'queue_music',
        color: '#1db954',
        label: 'Playing playlist'
    },
    spotify_play_by_mood: {
        icon: 'mood',
        color: '#1db954',
        label: 'Playing by mood'
    },
    spotify_pause: {
        icon: 'pause',
        color: '#1db954',
        label: 'Pausing Spotify'
    },
    spotify_resume: {
        icon: 'play_arrow',
        color: '#1db954',
        label: 'Resuming Spotify'
    },
    spotify_next: {
        icon: 'skip_next',
        color: '#1db954',
        label: 'Skipping to next'
    },
    spotify_previous: {
        icon: 'skip_previous',
        color: '#1db954',
        label: 'Going to previous'
    },
    spotify_set_volume: {
        icon: 'volume_up',
        color: '#1db954',
        label: 'Setting volume'
    },
    spotify_shuffle: {
        icon: 'shuffle',
        color: '#1db954',
        label: 'Toggling shuffle'
    },
    spotify_repeat: {
        icon: 'repeat',
        color: '#1db954',
        label: 'Setting repeat'
    },
    spotify_now_playing: {
        icon: 'radio',
        color: '#1db954',
        label: 'Getting now playing'
    },
    spotify_current_playback_details: {
        icon: 'info',
        color: '#1db954',
        label: 'Getting playback details'
    },
    spotify_add_to_queue: {
        icon: 'add_to_queue',
        color: '#1db954',
        label: 'Adding to queue'
    },
    spotify_like_current_song: {
        icon: 'favorite',
        color: '#1db954',
        label: 'Liking song'
    },
    spotify_unlike_current_song: {
        icon: 'heart_broken',
        color: '#1db954',
        label: 'Unliking song'
    },
    spotify_create_playlist: {
        icon: 'playlist_add',
        color: '#1db954',
        label: 'Creating playlist'
    },
    spotify_add_current_to_playlist: {
        icon: 'playlist_add',
        color: '#1db954',
        label: 'Adding to playlist'
    },
    spotify_list_my_playlists: {
        icon: 'library_music',
        color: '#1db954',
        label: 'Listing playlists'
    },

    // ═══════════════════════════════════════════════════════════════════
    // YOUTUBE TOOLS
    // ═══════════════════════════════════════════════════════════════════
    youtube_open: {
        icon: 'smart_display',
        color: '#ff0000',
        label: 'Opening YouTube'
    },
    youtube_shortcut: {
        icon: 'keyboard',
        color: '#ff0000',
        label: 'YouTube shortcut'
    },
    open_youtube: {
        icon: 'open_in_new',
        color: '#ff0000',
        label: 'Opening YouTube'
    },
    play_youtube_video: {
        icon: 'play_circle',
        color: '#ff0000',
        label: 'Playing YouTube video'
    },
    show_love_feels: {
        icon: 'favorite',
        color: '#ff69b4',
        label: 'Showing how love feels 💕'
    },
    youtube_search_and_play: {
        icon: 'search',
        color: '#ff0000',
        label: 'Searching YouTube'
    },
    youtube_play_by_url: {
        icon: 'link',
        color: '#ff0000',
        label: 'Playing YouTube URL'
    },
    youtube_control_playback: {
        icon: 'settings_remote',
        color: '#ff0000',
        label: 'Controlling YouTube'
    },
    youtube_find_live_streams: {
        icon: 'live_tv',
        color: '#ff0000',
        label: 'Finding live streams'
    },

    // ═══════════════════════════════════════════════════════════════════
    // COMPUTER USE / VISION AI TOOLS
    // ═══════════════════════════════════════════════════════════════════
    computer_use_spotify: {
        icon: 'visibility',
        color: '#8b5cf6',
        label: 'Vision: Spotify control'
    },
    computer_use_youtube: {
        icon: 'visibility',
        color: '#8b5cf6',
        label: 'Vision: YouTube control'
    },
    music_intent_router: {
        icon: 'route',
        color: '#8b5cf6',
        label: 'Routing music request'
    },

    // ═══════════════════════════════════════════════════════════════════
    // BROWSER AUTOMATION TOOLS
    // ═══════════════════════════════════════════════════════════════════
    web_automate: {
        icon: 'auto_fix_high',
        color: '#06b6d4',
        label: 'Automating browser'
    },
    browser_navigate_and_analyze: {
        icon: 'travel_explore',
        color: '#06b6d4',
        label: 'Analyzing webpage'
    },
    fill_web_form: {
        icon: 'edit_document',
        color: '#06b6d4',
        label: 'Filling form'
    },
    browser_extract_data: {
        icon: 'data_object',
        color: '#06b6d4',
        label: 'Extracting data'
    },

    // ═══════════════════════════════════════════════════════════════════
    // SOCIAL MEDIA TOOLS (from social_automation.py)
    // ═══════════════════════════════════════════════════════════════════
    // Instagram
    instagram_open_profile: {
        icon: 'person',
        color: '#e1306c',
        label: 'Opening Instagram profile'
    },
    instagram_send_dm: {
        icon: 'send',
        color: '#e1306c',
        label: 'Sending Instagram DM'
    },
    instagram_search_and_dm: {
        icon: 'person_search',
        color: '#e1306c',
        label: 'Searching & DMing'
    },
    instagram_like_recent_posts: {
        icon: 'favorite',
        color: '#e1306c',
        label: 'Liking posts'
    },
    instagram_follow_user: {
        icon: 'person_add',
        color: '#e1306c',
        label: 'Following user'
    },
    instagram_quick_dm: {
        icon: 'quickreply',
        color: '#e1306c',
        label: 'Quick Instagram DM'
    },

    // Twitter/X
    twitter_send_dm: {
        icon: 'send',
        color: '#1da1f2',
        label: 'Sending Twitter DM'
    },
    twitter_post_tweet: {
        icon: 'edit',
        color: '#1da1f2',
        label: 'Posting tweet'
    },

    // WhatsApp
    whatsapp_send_message: {
        icon: 'chat',
        color: '#25d366',
        label: 'Sending WhatsApp message'
    },
    whatsapp_send_to_number: {
        icon: 'phone',
        color: '#25d366',
        label: 'WhatsApp to number'
    },

    // LinkedIn
    linkedin_send_message: {
        icon: 'send',
        color: '#0a66c2',
        label: 'Sending LinkedIn message'
    },

    // Universal Social
    social_dm: {
        icon: 'forum',
        color: '#8b5cf6',
        label: 'Sending social DM'
    },

    // ═══════════════════════════════════════════════════════════════════
    // LEGACY / MISC TOOLS
    // ═══════════════════════════════════════════════════════════════════
    get_current_time: {
        icon: 'schedule',
        color: '#b1c5ff',
        label: 'Getting current time'
    },
    calculate: {
        icon: 'calculate',
        color: '#b1c5ff',
        label: 'Calculating'
    },
    notion_create_page: {
        icon: 'note_add',
        color: '#000000',
        label: 'Creating Notion page'
    },
    notion_search: {
        icon: 'search',
        color: '#000000',
        label: 'Searching Notion'
    },
    browser_navigate: {
        icon: 'public',
        color: '#8b5cf6',
        label: 'Navigating browser'
    },
    take_screenshot: {
        icon: 'screenshot',
        color: '#ec4899',
        label: 'Taking screenshot'
    }
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
 * Main Nivora Chat class (Enhanced with Tools)
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

    _setState(newState) {
        const oldState = this.state;
        this.state = newState;
        if (oldState !== newState) {
            this.emit('stateChange', { oldState, newState });
        }
    }

    /**
     * Send a message and get a response WITH TOOL SUPPORT
     */
    async sendMessage(message) {
        if (!message || !message.trim()) {
            throw new Error('Empty message');
        }

        if (this.state === ChatState.SENDING || this.state === ChatState.RECEIVING) {
            throw new Error('Already processing a message');
        }

        this._setState(ChatState.SENDING);
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

            // Emit tool calls if any
            if (data.tool_calls && data.tool_calls.length > 0) {
                this.emit('toolCalls', { tools: data.tool_calls });
            }

            // Add to local history
            this.messages.push({
                role: 'assistant',
                text: data.reply,
                tool_calls: data.tool_calls || [],
                timestamp: Date.now()
            });

            this._setState(ChatState.IDLE);

            return {
                reply: data.reply,
                tool_calls: data.tool_calls || []
            };

        } catch (error) {
            console.error('Chat error:', error);
            this._setState(ChatState.ERROR);
            this.emit('error', { message: error.message, type: 'send' });
            throw error;
        }
    }

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

        this.messages = [];
        this.sessionId = this._loadOrCreateSession();
        this.emit('historyCleared', {});
    }

    getState() {
        return {
            state: this.state,
            sessionId: this.sessionId,
            messageCount: this.messages.length,
            isProcessing: this.state === ChatState.SENDING || this.state === ChatState.RECEIVING
        };
    }

    getHistory() {
        return [...this.messages];
    }
}

/**
 * Enhanced Nivora Chat UI Controller WITH TOOL ANIMATIONS
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
            ...options
        };

        this.elements = {};
        this.hasStartedChat = false;

        this._onSendClick = this._onSendClick.bind(this);
        this._onKeyDown = this._onKeyDown.bind(this);
    }

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
        this.chat.on('toolCalls', ({ tools }) => this._showToolCalls(tools));

        console.log('NivoraChatUI initialized (ENHANCED with tools)');
    }

    async _onSendClick(e) {
        e?.preventDefault();

        const input = this.elements.input;
        if (!input) return;

        const text = input.value.trim();
        if (!text) return;

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

        // Show thinking indicator
        this._showThinkingIndicator();

        try {
            // Send message and get response WITH TOOLS
            const result = await this.chat.sendMessage(text);

            // Remove thinking indicator
            this._hideThinkingIndicator();

            // Show tool calls with animations (if any)
            if (result.tool_calls && result.tool_calls.length > 0) {
                await this._animateToolCalls(result.tool_calls);
            }

            // Show final response
            this._addMessage(result.reply, 'agent');

        } catch (error) {
            this._hideThinkingIndicator();
            this._showError(error.message || 'Failed to get response');
        }
    }

    /**
     * TOOL ANIMATION - Beautiful animated tool call display
     */
    async _animateToolCalls(toolCalls) {
        for (const tool of toolCalls) {
            await this._showSingleToolAnimation(tool);
            await this._sleep(500); // Brief pause between tools
        }
    }

    async _showSingleToolAnimation(tool) {
        if (!this.elements.messages) return;

        const metadata = TOOL_METADATA[tool.name] || {
            icon: 'build',
            color: '#b1c5ff',
            label: tool.name
        };

        // Create tool animation container
        const toolDiv = document.createElement('div');
        toolDiv.className = 'tool-call-animation flex justify-start mb-4 animate-fadeIn';
        toolDiv.innerHTML = `
            <div class="flex gap-4 items-center max-w-[90%]">
                <!-- Tool Icon with pulse animation -->
                <div class="flex-shrink-0 relative">
                    <div class="w-10 h-10 rounded-xl flex items-center justify-center tool-pulse" style="background: linear-gradient(135deg, ${metadata.color}20, ${metadata.color}10);">
                        <span class="material-symbols-outlined text-[20px]" style="color: ${metadata.color};">${metadata.icon}</span>
                    </div>
                    <!-- Animated rings -->
                    <div class="absolute inset-0 rounded-xl tool-ring" style="border: 2px solid ${metadata.color};"></div>
                    <div class="absolute inset-0 rounded-xl tool-ring-delayed" style="border: 2px solid ${metadata.color};"></div>
                </div>

                <!-- Tool info -->
                <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-xs font-semibold uppercase tracking-wider" style="color: ${metadata.color};">${metadata.label}</span>
                        <div class="flex gap-1">
                            <span class="w-1 h-1 rounded-full bg-primary animate-bounce" style="animation-delay: 0s;"></span>
                            <span class="w-1 h-1 rounded-full bg-primary animate-bounce" style="animation-delay: 0.2s;"></span>
                            <span class="w-1 h-1 rounded-full bg-primary animate-bounce" style="animation-delay: 0.4s;"></span>
                        </div>
                    </div>
                    <div class="text-sm text-on-surface-variant/70 font-mono">
                        ${this._formatToolInput(tool.input)}
                    </div>
                </div>
            </div>
        `;

        this.elements.messages.appendChild(toolDiv);
        this._scrollToBottom();

        // Wait for animation to complete
        await this._sleep(1500);

        // Add completion checkmark
        const icon = toolDiv.querySelector('.material-symbols-outlined');
        if (icon) {
            icon.textContent = 'check_circle';
            icon.style.color = '#4ade80'; // Green
        }

        // Stop animations
        toolDiv.querySelectorAll('.tool-pulse, .tool-ring, .tool-ring-delayed').forEach(el => {
            el.style.animation = 'none';
        });

        await this._sleep(800);
    }

    _formatToolInput(input) {
        if (typeof input === 'string') return this._escapeHtml(input);
        const entries = Object.entries(input);
        if (entries.length === 1) {
            return this._escapeHtml(String(entries[0][1]));
        }
        return entries.map(([k, v]) => `${k}: ${this._escapeHtml(String(v))}`).join(', ');
    }

    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    _transformToChatMode() {
        this.hasStartedChat = true;
        document.body.classList.add('chat-started');

        if (this.elements.inputContainer) {
            this.elements.inputContainer.classList.add('input-compact');
        }

        if (this.elements.quickActions) {
            this.elements.quickActions.style.display = 'none';
        }

        if (this.elements.chatWrapper) {
            this.elements.chatWrapper.classList.remove('chat-centered');
            this.elements.chatWrapper.classList.add('chat-active');
        }

        if (this.elements.input) {
            this.elements.input.placeholder = 'Message Nivora...';
        }
    }

    _onKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this._onSendClick();
        }
    }

    _addMessage(text, speaker) {
        if (!this.elements.messages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${speaker} animate-fadeIn`;

        const isUser = speaker === 'user';

        if (isUser) {
            messageDiv.innerHTML = `
                <div class="flex justify-end mb-4">
                    <div class="bg-surface-container-high px-4 py-3 rounded-2xl max-w-[80%]">
                        <p class="text-sm text-on-surface leading-relaxed whitespace-pre-wrap">${this._escapeHtml(text)}</p>
                    </div>
                </div>
            `;
        } else {
            const renderedContent = this._renderMarkdown(text);
            messageDiv.innerHTML = `
                <div class="flex justify-start mb-6">
                    <div class="flex gap-3 max-w-[90%]">
                        <!-- Nivora Avatar with Logo -->
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

    _renderMarkdown(text) {
        if (typeof marked !== 'undefined') {
            try {
                return marked.parse(text);
            } catch (e) {
                console.warn('Markdown parsing failed:', e);
            }
        }
        return this._escapeHtml(text)
            .replace(/\n/g, '<br>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/\*([^*]+)\*/g, '<em>$1</em>');
    }

    _showThinkingIndicator() {
        if (!this.elements.messages) return;

        const indicator = document.createElement('div');
        indicator.className = `${this.options.typingIndicatorClass} flex justify-start mb-6 animate-fadeIn`;
        indicator.innerHTML = `
            <div class="flex gap-4 items-start">
                <!-- Nivora Avatar with Spinning Ring -->
                <div class="flex-shrink-0 relative w-12 h-12">
                    <svg class="w-12 h-12 thinking-ring absolute inset-0" viewBox="0 0 48 48">
                        <circle cx="24" cy="24" r="20" fill="none" stroke="#434653" stroke-width="2" opacity="0.3"/>
                        <line x1="24" y1="4" x2="24" y2="14" stroke="#b1c5ff" stroke-width="2" stroke-linecap="round"/>
                        <line x1="24" y1="34" x2="24" y2="44" stroke="#b1c5ff" stroke-width="2" stroke-linecap="round"/>
                        <line x1="4" y1="24" x2="14" y2="24" stroke="#b1c5ff" stroke-width="2" stroke-linecap="round"/>
                        <line x1="34" y1="24" x2="44" y2="24" stroke="#b1c5ff" stroke-width="2" stroke-linecap="round"/>
                        <circle cx="24" cy="4" r="3" fill="#b1c5ff"/>
                        <circle cx="24" cy="44" r="3" fill="#b1c5ff"/>
                        <circle cx="4" cy="24" r="3" fill="#b1c5ff"/>
                        <circle cx="44" cy="24" r="3" fill="#b1c5ff"/>
                    </svg>
                    <div class="absolute inset-0 flex items-center justify-center">
                        <div class="w-6 h-6 rounded-full bg-surface-container flex items-center justify-center p-1">
                            <img src="assets/nivora-logo.png" alt="Nivora" class="w-full h-full object-contain"/>
                        </div>
                    </div>
                </div>
                <div class="flex flex-col justify-center pt-1">
                    <div class="text-[11px] text-primary/70 font-semibold uppercase tracking-wider mb-1">Nivora</div>
                    <div class="text-sm text-on-surface-variant">Thinking<span class="thinking-dots"></span></div>
                </div>
            </div>
        `;

        this.elements.messages.appendChild(indicator);
        this._scrollToBottom();
    }

    _hideThinkingIndicator() {
        const indicator = document.querySelector(`.${this.options.typingIndicatorClass}`);
        if (indicator) indicator.remove();
    }

    _showToolCalls(tools) {
        console.log('Tool calls detected:', tools);
    }

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

    _scrollToBottom() {
        if (this.elements.messages) {
            setTimeout(() => {
                this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
            }, 50);
        }
    }

    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

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
    const chat = new NivoraChat();
    const ui = new NivoraChatUI(chat);
    ui.init();

    window.nivoraChat = chat;
    window.nivoraChatUI = ui;

    console.log('✓ Nivora Chat ready (ENHANCED with tools)');
    console.log('  Available tools: 70+ tools including Spotify, YouTube, Email, Social Media, Browser Automation, and more');
}

// Export
window.NivoraChat = NivoraChat;
window.NivoraChatUI = NivoraChatUI;
window.ChatState = ChatState;
window.initNivoraChat = initNivoraChat;

// Auto-init
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNivoraChat);
} else {
    initNivoraChat();
}
