'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { useTheme } from 'next-themes';
import { AnimatePresence, motion } from 'motion/react';
import { useSessionContext, useSessionMessages } from '@livekit/components-react';
import { useAgent } from '@livekit/components-react';
import { Microphone } from '@phosphor-icons/react';
import { AgentAudioVisualizerAura } from '@/components/agents-ui/agent-audio-visualizer-aura';
import { AgentChatIndicator } from '@/components/agents-ui/agent-chat-indicator';
import { AgentChatTranscript } from '@/components/agents-ui/agent-chat-transcript';
import { AgentControlBar } from '@/components/agents-ui/agent-control-bar';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/shadcn/utils';

const MotionDiv = motion.create('div');

export function PlaygroundView() {
  const session = useSessionContext();
  const { messages } = useSessionMessages(session);
  const [chatOpen, setChatOpen] = useState(false);
  const { resolvedTheme: theme } = useTheme();
  const { audioTrack, state } = useAgent();

  const { isConnected } = session;

  if (!isConnected) {
    return <WelcomeScreen onConnect={session.start} />;
  }

  return (
    <div className="relative flex h-full w-full flex-col items-center justify-center">
      {/* Header */}
      <header className="border-border/40 bg-background/80 absolute top-0 right-0 left-0 z-10 flex items-center justify-between border-b px-6 py-4 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="bg-primary/10 flex h-8 w-8 items-center justify-center rounded-full">
            <span className="text-primary text-sm font-bold">LK</span>
          </div>
          <h1 className="text-lg font-semibold">Voice Assistant Playground</h1>
        </div>
        <div className="flex items-center gap-2">
          <ConnectionStatus isConnected={isConnected} />
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex h-full w-full flex-col items-center justify-center pt-20 pb-32">
        {/* Visualizer Area */}
        <div className="flex flex-col items-center justify-center gap-16">
          {/* Audio Visualizer */}
          <div className="relative flex h-64 w-64 items-center justify-center">
            <AgentAudioVisualizerAura
              size="lg"
              color="#f9811f"
              colorShift={0.1}
              state={state}
              themeMode={theme as 'light' | 'dark' | undefined}
              audioTrack={audioTrack}
            />
          </div>

          {/* Status Message */}
          <div className="text-center">
            {messages.length === 0 ? (
              <p className="text-muted-foreground text-sm">Agent is listening, start speaking...</p>
            ) : (
              <p className="text-muted-foreground text-sm">
                {String(messages[messages.length - 1]?.message || '').replace(/<thinking>[\s\S]*?(<\/thinking>|$)/gi, '').trim() || 'Thinking...'}
              </p>
            )}
          </div>
        </div>

        {/* Transcript Sidebar */}
        <AnimatePresence>
          {chatOpen && (
            <MotionDiv
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="border-border bg-background/95 absolute top-0 right-0 z-20 h-full w-96 border-l backdrop-blur-sm"
            >
              <div className="flex h-full flex-col">
                <div className="border-border flex items-center justify-between border-b px-6 py-4">
                  <h2 className="text-lg font-semibold">Transcript</h2>
                  <Button variant="ghost" size="sm" onClick={() => setChatOpen(false)}>
                    ×
                  </Button>
                </div>
                <div className="relative flex-1 overflow-hidden p-6">
                  <AgentChatTranscript agentState={state} messages={messages} />
                </div>
              </div>
            </MotionDiv>
          )}
        </AnimatePresence>
      </div>

      {/* Control Bar */}
      <div className="absolute bottom-8 left-1/2 z-30 -translate-x-1/2">
        <div className="border-border/40 bg-background/80 flex items-center gap-3 rounded-full border px-6 py-3 shadow-lg backdrop-blur-sm">
          <AgentControlBar
            variant="livekit"
            controls={{
              microphone: true,
              chat: true,
              leave: true,
              camera: false,
              screenShare: false,
            }}
            isChatOpen={chatOpen}
            isConnected={session.isConnected}
            onDisconnect={session.end}
            onIsChatOpenChange={setChatOpen}
          />
        </div>
      </div>
    </div>
  );
}

// Floating Particle interface
interface Particle {
  id: number;
  x: number;
  y: number;
  size: number;
  color: string;
  vx: number;
  vy: number;
  opacity: number;
  blur: number;
}

// AI Model logos for the marquee (from public folder)
const AI_MODEL_LOGOS = [
  { name: 'Claude', logo: '/claude-3.svg' },
  { name: 'ChatGPT', logo: '/chatgpt-3.svg' },
  { name: 'Gemini', logo: '/gemini-ai.svg' },
  { name: 'Perplexity', logo: '/perplexity-3.svg' },
  { name: 'DeepSeek', logo: '/deepseek-ai-seeklogo.svg' },
  { name: 'Groq', logo: '/groq-logo.png' },
  { name: 'Qwen', logo: '/Qwen_Logo.svg' },
  { name: 'Meta', logo: '/meta-3.svg' },
  { name: 'Azure', logo: '/microsoft-azure-2.svg' },
  { name: 'AWS', logo: '/aws-2.svg' },
  { name: 'LiveKit', logo: '/lk-logo.svg' },
];

// Welcome Screen Component with Aurora effect
function WelcomeScreen({ onConnect }: { onConnect: () => void }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const animationRef = useRef<number>(0);
  const [isHovered, setIsHovered] = useState(false);
  const [typedText, setTypedText] = useState('');
  const tagline = 'Your AI companion, codenamed Friday';

  // Typing effect
  useEffect(() => {
    let index = 0;
    const delay = setTimeout(() => {
      const interval = setInterval(() => {
        if (index <= tagline.length) {
          setTypedText(tagline.slice(0, index));
          index++;
        } else {
          clearInterval(interval);
        }
      }, 50);
      return () => clearInterval(interval);
    }, 800);
    return () => clearTimeout(delay);
  }, []);

  // Create particles
  const createParticle = (width: number, height: number, id: number): Particle => {
    const colors = [
      'rgba(0, 229, 255, 0.6)', // Cyan
      'rgba(127, 0, 255, 0.5)', // Purple
      'rgba(75, 0, 130, 0.4)', // Indigo
      'rgba(0, 191, 255, 0.5)', // Deep Sky Blue
      'rgba(148, 0, 211, 0.4)', // Dark Violet
      'rgba(138, 43, 226, 0.5)', // Blue Violet
    ];

    return {
      id,
      x: Math.random() * width,
      y: Math.random() * height,
      size: Math.random() * 80 + 20,
      color: colors[Math.floor(Math.random() * colors.length)],
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      opacity: Math.random() * 0.5 + 0.2,
      blur: Math.random() * 40 + 20,
    };
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      const dpr = window.devicePixelRatio || 1;
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      canvas.style.width = `${window.innerWidth}px`;
      canvas.style.height = `${window.innerHeight}px`;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);

      // Initialize particles
      particlesRef.current = [];
      for (let i = 0; i < 25; i++) {
        particlesRef.current.push(createParticle(window.innerWidth, window.innerHeight, i));
      }
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const animate = () => {
      if (!canvas || !ctx) return;

      // Dark gradient background
      const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
      gradient.addColorStop(0, '#0a0a0f');
      gradient.addColorStop(0.5, '#0d0d15');
      gradient.addColorStop(1, '#0a0a0f');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);

      // Draw and update particles
      particlesRef.current.forEach((particle) => {
        // Update position
        particle.x += particle.vx;
        particle.y += particle.vy;

        // Wrap around edges
        if (particle.x < -particle.size) particle.x = window.innerWidth + particle.size;
        if (particle.x > window.innerWidth + particle.size) particle.x = -particle.size;
        if (particle.y < -particle.size) particle.y = window.innerHeight + particle.size;
        if (particle.y > window.innerHeight + particle.size) particle.y = -particle.size;

        // Draw particle with blur effect
        ctx.save();
        ctx.filter = `blur(${particle.blur}px)`;
        ctx.globalAlpha = particle.opacity;

        const particleGradient = ctx.createRadialGradient(
          particle.x,
          particle.y,
          0,
          particle.x,
          particle.y,
          particle.size
        );
        particleGradient.addColorStop(0, particle.color);
        particleGradient.addColorStop(1, 'transparent');

        ctx.fillStyle = particleGradient;
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationRef.current);
    };
  }, []);

  return (
    <div className="relative flex h-full w-full flex-col items-center justify-center overflow-hidden">
      {/* Animated particle background */}
      <canvas ref={canvasRef} className="absolute inset-0 z-0" />

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center justify-center gap-4 px-6 pb-32">
        {/* Nivora Logo with glow */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8, rotate: -180 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          transition={{
            duration: 1.2,
            ease: [0.19, 1, 0.22, 1],
            rotate: { duration: 1.5, ease: 'easeOut' },
          }}
          className="relative mb-4"
        >
          {/* Glow effect */}
          <motion.div
            className="absolute inset-[-20px] rounded-full"
            style={{
              background: 'radial-gradient(circle, rgba(0, 229, 255, 0.3) 0%, transparent 70%)',
            }}
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
          {/* Rotating logo */}
          <motion.img
            src="/WhatsApp Image 2026-03-29 at 19.06.46.jpeg"
            alt="Nivora Logo"
            className="relative z-10 h-32 w-32 rounded-full object-cover md:h-40 md:w-40"
            style={{
              boxShadow: '0 0 40px rgba(0, 229, 255, 0.4), 0 0 80px rgba(127, 0, 255, 0.2)',
            }}
            animate={{ rotate: 360 }}
            transition={{
              duration: 60,
              repeat: Infinity,
              ease: 'linear',
            }}
          />
          {/* Pulse rings */}
          <div
            className="absolute inset-[-8px] animate-ping rounded-full border border-cyan-400/20"
            style={{ animationDuration: '3s' }}
          />
          <div
            className="absolute inset-[-20px] animate-ping rounded-full border border-purple-400/10"
            style={{ animationDuration: '3s', animationDelay: '1.5s' }}
          />
        </motion.div>

        {/* Main Title with Aurora Effect */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3, ease: 'easeOut' }}
          className="text-center"
        >
          <h1
            className="aurora-text text-4xl font-light tracking-tight md:text-5xl lg:text-6xl"
            style={{
              fontFamily: "'Source Serif 4', Georgia, serif",
              letterSpacing: '-0.02em',
            }}
          >
            Meet Nivora
          </h1>
        </motion.div>

        {/* Subtitle with typing effect */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.6, ease: 'easeOut' }}
          className="min-h-[24px] text-sm font-light text-cyan-300/60 md:text-base"
          style={{ fontFamily: "'Inter', sans-serif" }}
        >
          {typedText}
          <span className="animate-pulse text-cyan-400">|</span>
        </motion.p>

        {/* Developer credit */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4, ease: 'easeOut' }}
          className="text-sm font-medium tracking-[0.25em] text-white/40 uppercase md:text-base"
        >
          Developed by Anbu Infin
        </motion.p>

        {/* CTA Button - Gemini style with glow */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8, ease: 'easeOut' }}
          className="mt-2"
        >
          <motion.button
            onClick={onConnect}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            className="group relative overflow-hidden rounded-full px-8 py-3 transition-all duration-500"
            style={{
              background: 'linear-gradient(135deg, #00BFFF 0%, #1E90FF 50%, #00CED1 100%)',
              boxShadow: isHovered
                ? '0 0 30px rgba(0, 191, 255, 0.6), 0 0 60px rgba(30, 144, 255, 0.4), 0 0 90px rgba(0, 206, 209, 0.2)'
                : '0 0 20px rgba(0, 191, 255, 0.4), 0 0 40px rgba(30, 144, 255, 0.2)',
            }}
            whileHover={{
              scale: 1.05,
            }}
            whileTap={{ scale: 0.98 }}
          >
            {/* Animated shine effect */}
            <motion.div
              className="absolute inset-0 opacity-0 group-hover:opacity-100"
              style={{
                background:
                  'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
              }}
              animate={{
                x: isHovered ? ['-100%', '100%'] : '-100%',
              }}
              transition={{
                duration: 0.8,
                ease: 'easeInOut',
              }}
            />
            <span
              className="relative z-10 flex items-center gap-3"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              <span
                className="text-sm font-bold tracking-[0.2em] uppercase"
                style={{
                  background:
                    'linear-gradient(90deg, #ffffff 0%, #e0f7ff 25%, #ffffff 50%, #b3ecff 75%, #ffffff 100%)',
                  backgroundSize: '200% 100%',
                  WebkitBackgroundClip: 'text',
                  backgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  animation: 'textShimmer 3s ease-in-out infinite',
                  textShadow: '0 0 20px rgba(255, 255, 255, 0.5)',
                }}
              >
                Wanna Talk?
              </span>
            </span>
          </motion.button>
        </motion.div>
      </div>

      {/* Bottom Section - Powered by AI Models */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 1.0, ease: 'easeOut' }}
        className="absolute right-0 bottom-6 left-0 z-10"
      >
        <p
          className="mb-4 text-center text-xs tracking-[0.15em] text-white/30 uppercase"
          style={{ fontFamily: "'Inter', sans-serif" }}
        >
          Powered by Leading AI Models
        </p>

        {/* Infinite Marquee with Logos */}
        <div className="marquee-wrapper w-full">
          <div className="marquee-track">
            {/* First set of logos */}
            {AI_MODEL_LOGOS.map((model, idx) => (
              <div key={`first-${idx}`} className="flex items-center justify-center px-8">
                <img
                  src={model.logo}
                  alt={model.name}
                  className="h-7 w-auto opacity-40 transition-all duration-300 hover:opacity-100"
                  style={{ filter: 'brightness(0) invert(1)', maxWidth: '80px' }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.filter = 'none';
                    e.currentTarget.style.opacity = '1';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.filter = 'brightness(0) invert(1)';
                    e.currentTarget.style.opacity = '0.4';
                  }}
                />
              </div>
            ))}
            {/* Duplicate for seamless loop */}
            {AI_MODEL_LOGOS.map((model, idx) => (
              <div key={`second-${idx}`} className="flex items-center justify-center px-8">
                <img
                  src={model.logo}
                  alt={model.name}
                  className="h-7 w-auto opacity-40 transition-all duration-300 hover:opacity-100"
                  style={{ filter: 'brightness(0) invert(1)', maxWidth: '80px' }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.filter = 'none';
                    e.currentTarget.style.opacity = '1';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.filter = 'brightness(0) invert(1)';
                    e.currentTarget.style.opacity = '0.4';
                  }}
                />
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}

// Connection Status Component
function ConnectionStatus({ isConnected }: { isConnected: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <div className={cn('h-2 w-2 rounded-full', isConnected ? 'bg-green-500' : 'bg-yellow-500')} />
      <span className="text-muted-foreground text-sm">
        {isConnected ? 'Connected' : 'Connecting...'}
      </span>
    </div>
  );
}
