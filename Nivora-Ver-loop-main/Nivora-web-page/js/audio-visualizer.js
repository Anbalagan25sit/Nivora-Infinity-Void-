/**
 * Nivora Audio Visualizer
 *
 * Provides visual feedback for audio activity including:
 * - Orb pulsing based on audio levels
 * - Waveform visualization
 * - Speaking indicators
 */

class NivoraAudioVisualizer {
    constructor(options = {}) {
        this.options = {
            orbSelector: '#orb-container',
            waveformSelector: '#waveform',
            canvasSelector: '#audio-canvas',
            sensitivity: 1.5,
            smoothing: 0.8,
            minScale: 1.0,
            maxScale: 1.3,
            ...options
        };

        this.orb = null;
        this.canvas = null;
        this.ctx = null;
        this.analyser = null;
        this.animationFrame = null;
        this.isRunning = false;

        // Smoothed values
        this.smoothedLevel = 0;
        this.smoothedPeak = 0;

        // Bind methods
        this._animate = this._animate.bind(this);
    }

    /**
     * Initialize the visualizer
     */
    init() {
        this.orb = document.querySelector(this.options.orbSelector);
        this.canvas = document.querySelector(this.options.canvasSelector);

        if (this.canvas) {
            this.ctx = this.canvas.getContext('2d');
            this._resizeCanvas();
            window.addEventListener('resize', () => this._resizeCanvas());
        }

        console.log('Audio visualizer initialized');
    }

    /**
     * Connect to an audio analyser node
     */
    connectAnalyser(analyser) {
        this.analyser = analyser;
        this.start();
    }

    /**
     * Create analyser from MediaStream
     */
    connectStream(stream) {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContext.createMediaStreamSource(stream);
        this.analyser = audioContext.createAnalyser();
        this.analyser.fftSize = 256;
        this.analyser.smoothingTimeConstant = this.options.smoothing;

        source.connect(this.analyser);
        this.start();

        return this.analyser;
    }

    /**
     * Start animation loop
     */
    start() {
        if (this.isRunning) return;
        this.isRunning = true;
        this._animate();
    }

    /**
     * Stop animation loop
     */
    stop() {
        this.isRunning = false;
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
            this.animationFrame = null;
        }

        // Reset visual state
        this._resetVisuals();
    }

    /**
     * Main animation loop
     */
    _animate() {
        if (!this.isRunning) return;

        // Get audio data
        const levels = this._getAudioLevels();

        // Smooth the values
        this.smoothedLevel = this._lerp(this.smoothedLevel, levels.average, 0.2);
        this.smoothedPeak = this._lerp(this.smoothedPeak, levels.peak, 0.15);

        // Update visualizations
        this._updateOrb();
        this._updateCanvas(levels.frequencies);

        this.animationFrame = requestAnimationFrame(this._animate);
    }

    /**
     * Get current audio levels from analyser
     */
    _getAudioLevels() {
        if (!this.analyser) {
            return { average: 0, peak: 0, frequencies: [] };
        }

        const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
        this.analyser.getByteFrequencyData(dataArray);

        let sum = 0;
        let peak = 0;

        for (let i = 0; i < dataArray.length; i++) {
            sum += dataArray[i];
            if (dataArray[i] > peak) peak = dataArray[i];
        }

        return {
            average: (sum / dataArray.length / 255) * this.options.sensitivity,
            peak: (peak / 255) * this.options.sensitivity,
            frequencies: Array.from(dataArray)
        };
    }

    /**
     * Update orb visualization
     */
    _updateOrb() {
        if (!this.orb) return;

        // Calculate scale based on audio level
        const scale = this.options.minScale +
            (this.smoothedLevel * (this.options.maxScale - this.options.minScale));

        // Calculate glow intensity
        const glowIntensity = Math.min(1, this.smoothedPeak * 1.5);
        const glowSize = 40 + (glowIntensity * 40);

        // Apply to orb core (innermost circle)
        const orbCore = this.orb.querySelector('.orb-core, [class*="w-16"][class*="h-16"]');
        if (orbCore) {
            orbCore.style.transform = `scale(${scale})`;
            orbCore.style.boxShadow = `0 0 ${glowSize}px rgba(177, 197, 255, ${0.4 + glowIntensity * 0.4})`;
            orbCore.style.transition = 'transform 0.1s ease-out, box-shadow 0.1s ease-out';
        }

        // Update outer rings
        const rings = this.orb.querySelectorAll('[class*="border-primary"]');
        rings.forEach((ring, index) => {
            const ringScale = 1 + (this.smoothedLevel * 0.1 * (index + 1));
            const opacity = 0.2 + (this.smoothedLevel * 0.3);
            ring.style.transform = `scale(${ringScale})`;
            ring.style.opacity = opacity;
            ring.style.transition = 'transform 0.15s ease-out, opacity 0.15s ease-out';
        });

        // Update blur glow
        const blur = this.orb.querySelector('[class*="blur-2xl"]');
        if (blur) {
            const blurScale = 1 + (this.smoothedPeak * 0.5);
            const blurOpacity = 0.2 + (this.smoothedPeak * 0.3);
            blur.style.transform = `scale(${blurScale})`;
            blur.style.opacity = blurOpacity;
        }
    }

    /**
     * Update canvas waveform visualization
     */
    _updateCanvas(frequencies) {
        if (!this.canvas || !this.ctx || frequencies.length === 0) return;

        const width = this.canvas.width;
        const height = this.canvas.height;
        const centerY = height / 2;

        // Clear canvas
        this.ctx.clearRect(0, 0, width, height);

        // Draw waveform
        this.ctx.beginPath();
        this.ctx.strokeStyle = `rgba(177, 197, 255, ${0.3 + this.smoothedLevel * 0.5})`;
        this.ctx.lineWidth = 2;

        const sliceWidth = width / frequencies.length;
        let x = 0;

        for (let i = 0; i < frequencies.length; i++) {
            const value = frequencies[i] / 255;
            const y = centerY + (value - 0.5) * height * 0.8;

            if (i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }

            x += sliceWidth;
        }

        this.ctx.stroke();

        // Draw bars visualization
        this._drawBars(frequencies);
    }

    /**
     * Draw frequency bars
     */
    _drawBars(frequencies) {
        if (!this.ctx) return;

        const width = this.canvas.width;
        const height = this.canvas.height;
        const barCount = 32;
        const barWidth = (width / barCount) * 0.6;
        const gap = (width / barCount) * 0.4;

        // Sample frequencies
        const step = Math.floor(frequencies.length / barCount);

        for (let i = 0; i < barCount; i++) {
            const value = frequencies[i * step] / 255;
            const barHeight = value * height * 0.4;

            const x = i * (barWidth + gap);
            const y = (height - barHeight) / 2;

            // Gradient for bars
            const gradient = this.ctx.createLinearGradient(0, y + barHeight, 0, y);
            gradient.addColorStop(0, 'rgba(177, 197, 255, 0.1)');
            gradient.addColorStop(1, `rgba(177, 197, 255, ${0.3 + value * 0.5})`);

            this.ctx.fillStyle = gradient;
            this.ctx.fillRect(x, y, barWidth, barHeight);
        }
    }

    /**
     * Resize canvas to match container
     */
    _resizeCanvas() {
        if (!this.canvas) return;

        const parent = this.canvas.parentElement;
        if (parent) {
            this.canvas.width = parent.clientWidth;
            this.canvas.height = parent.clientHeight;
        } else {
            this.canvas.width = window.innerWidth;
            this.canvas.height = 200;
        }
    }

    /**
     * Reset visuals to default state
     */
    _resetVisuals() {
        if (this.orb) {
            const orbCore = this.orb.querySelector('.orb-core, [class*="w-16"][class*="h-16"]');
            if (orbCore) {
                orbCore.style.transform = 'scale(1)';
                orbCore.style.boxShadow = '0 0 40px rgba(177, 197, 255, 0.4)';
            }

            const rings = this.orb.querySelectorAll('[class*="border-primary"]');
            rings.forEach(ring => {
                ring.style.transform = 'scale(1)';
                ring.style.opacity = '';
            });
        }

        if (this.ctx && this.canvas) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }

        this.smoothedLevel = 0;
        this.smoothedPeak = 0;
    }

    /**
     * Linear interpolation helper
     */
    _lerp(start, end, factor) {
        return start + (end - start) * factor;
    }

    /**
     * Set speaking state (agent speaking)
     */
    setSpeaking(isSpeaking) {
        if (!this.orb) return;

        if (isSpeaking) {
            this.orb.classList.add('speaking');
            // Add pulsing animation
            const orbCore = this.orb.querySelector('.orb-core, [class*="w-16"][class*="h-16"]');
            if (orbCore) {
                orbCore.style.animation = 'pulse-glow 1s ease-in-out infinite';
            }
        } else {
            this.orb.classList.remove('speaking');
            const orbCore = this.orb.querySelector('.orb-core, [class*="w-16"][class*="h-16"]');
            if (orbCore) {
                orbCore.style.animation = '';
            }
        }
    }

    /**
     * Set listening state (user speaking)
     */
    setListening(isListening) {
        if (!this.orb) return;

        if (isListening) {
            this.orb.classList.add('listening');
        } else {
            this.orb.classList.remove('listening');
        }
    }

    /**
     * Cleanup
     */
    destroy() {
        this.stop();
        window.removeEventListener('resize', () => this._resizeCanvas());
    }
}

/**
 * Microphone audio level monitor
 * For showing user's voice activity without full LiveKit connection
 */
class MicrophoneLevelMonitor {
    constructor(callback) {
        this.callback = callback;
        this.audioContext = null;
        this.analyser = null;
        this.microphone = null;
        this.stream = null;
        this.animationFrame = null;
        this.isRunning = false;
    }

    /**
     * Start monitoring microphone levels
     */
    async start() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            this.analyser.smoothingTimeConstant = 0.8;

            this.microphone = this.audioContext.createMediaStreamSource(this.stream);
            this.microphone.connect(this.analyser);

            this.isRunning = true;
            this._monitor();

            return true;
        } catch (error) {
            console.error('Microphone access error:', error);
            return false;
        }
    }

    /**
     * Monitor loop
     */
    _monitor() {
        if (!this.isRunning) return;

        const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
        this.analyser.getByteFrequencyData(dataArray);

        let sum = 0;
        let peak = 0;
        for (let i = 0; i < dataArray.length; i++) {
            sum += dataArray[i];
            if (dataArray[i] > peak) peak = dataArray[i];
        }

        const level = sum / dataArray.length / 255;
        const peakLevel = peak / 255;

        if (this.callback) {
            this.callback({ level, peak: peakLevel, isSpeaking: level > 0.05 });
        }

        this.animationFrame = requestAnimationFrame(() => this._monitor());
    }

    /**
     * Stop monitoring
     */
    stop() {
        this.isRunning = false;

        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }

        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }

        if (this.audioContext) {
            this.audioContext.close();
        }

        this.audioContext = null;
        this.analyser = null;
        this.microphone = null;
        this.stream = null;
    }
}

// Export
window.NivoraAudioVisualizer = NivoraAudioVisualizer;
window.MicrophoneLevelMonitor = MicrophoneLevelMonitor;

// Auto-initialize if orb container exists
document.addEventListener('DOMContentLoaded', () => {
    const orbContainer = document.querySelector('#orb-container, .orb-container');
    if (orbContainer) {
        const visualizer = new NivoraAudioVisualizer({
            orbSelector: '#orb-container, .orb-container'
        });
        visualizer.init();

        // Connect to nivoraVoice if available
        if (window.nivoraVoice) {
            window.nivoraVoice.on('analyzerReady', ({ analyser }) => {
                visualizer.connectAnalyser(analyser);
            });

            window.nivoraVoice.on('agentState', (state) => {
                visualizer.setSpeaking(state === AgentState.SPEAKING);
                visualizer.setListening(state === AgentState.LISTENING);
            });
        }

        window.nivoraVisualizer = visualizer;
    }
});
