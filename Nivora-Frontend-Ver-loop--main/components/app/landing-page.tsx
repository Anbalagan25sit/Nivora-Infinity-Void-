'use client';

import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import Image from 'next/image';

// =============================================================================
// NIVORA HERO LANDING PAGE - Premium Claude-Inspired Design
// =============================================================================

const CAPABILITIES = [
  { icon: '🎙️', title: 'Voice', color: '#00E5FF' },
  { icon: '🎵', title: 'Spotify', color: '#1DB954' },
  { icon: '🌐', title: 'Web', color: '#7F00FF' },
  { icon: '📨', title: 'Email', color: '#00BFFF' },
  { icon: '📊', title: 'Sheets', color: '#4285F4' },
  { icon: '💻', title: 'System', color: '#9400D3' },
];

// AI Model logos for the infinite scroll
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

// =============================================================================
// ANIMATED LOGO COMPONENT - Rotating Wheel
// =============================================================================

function AnimatedLogo() {
  return (
    <motion.div
      className="logo-container"
      initial={{ opacity: 0, scale: 0.8, rotate: -180 }}
      animate={{ opacity: 1, scale: 1, rotate: 0 }}
      transition={{
        duration: 1.2,
        ease: [0.19, 1, 0.22, 1],
        rotate: { duration: 1.5, ease: "easeOut" }
      }}
    >
      <motion.div
        className="logo-glow"
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.6, 0.3]
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      <motion.img
        src="/WhatsApp Image 2026-03-29 at 19.06.46.jpeg"
        alt="Nivora Logo"
        className="main-logo"
        animate={{
          rotate: 360,
        }}
        transition={{
          duration: 60,
          repeat: Infinity,
          ease: "linear"
        }}
      />
      <div className="logo-ring" />
      <div className="logo-ring logo-ring-2" />
    </motion.div>
  );
}

// =============================================================================
// FLOATING PARTICLES BACKGROUND
// =============================================================================

function ParticleField() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId: number;
    let particles: Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      size: number;
      opacity: number;
      color: string;
    }> = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initParticles();
    };

    const initParticles = () => {
      particles = [];
      const count = Math.floor((canvas.width * canvas.height) / 15000);
      const colors = ['#00E5FF', '#7F00FF', '#00BFFF', '#9400D3'];
      for (let i = 0; i < count; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.3,
          vy: (Math.random() - 0.5) * 0.3,
          size: Math.random() * 2 + 0.5,
          opacity: Math.random() * 0.5 + 0.1,
          color: colors[Math.floor(Math.random() * colors.length)],
        });
      }
    };

    const animate = () => {
      ctx.fillStyle = 'rgba(28, 25, 23, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.color.replace(')', `, ${p.opacity})`).replace('rgb', 'rgba');
        ctx.fill();
      });

      // Draw connections
      particles.forEach((p1, i) => {
        particles.slice(i + 1).forEach((p2) => {
          const dx = p1.x - p2.x;
          const dy = p1.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 100) {
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(0, 229, 255, ${0.1 * (1 - dist / 100)})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        });
      });

      animationId = requestAnimationFrame(animate);
    };

    resize();
    window.addEventListener('resize', resize);
    animate();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return <canvas ref={canvasRef} className="particle-canvas" />;
}

// =============================================================================
// MAIN LANDING PAGE COMPONENT
// =============================================================================

export interface LandingPageProps {
  onStartCall: () => void;
}

export function LandingPage({ onStartCall }: LandingPageProps) {
  const [mounted, setMounted] = useState(false);
  const [typedText, setTypedText] = useState('');
  const tagline = 'Your AI companion, codenamed Friday';

  useEffect(() => {
    setMounted(true);
  }, []);

  // Typing effect
  useEffect(() => {
    if (!mounted) return;

    const delay = setTimeout(() => {
      let index = 0;
      const interval = setInterval(() => {
        if (index <= tagline.length) {
          setTypedText(tagline.slice(0, index));
          index++;
        } else {
          clearInterval(interval);
        }
      }, 50);

      return () => clearInterval(interval);
    }, 1200);

    return () => clearTimeout(delay);
  }, [mounted]);

  if (!mounted) return null;

  return (
    <div className="nivora-landing">
      {/* Google Fonts */}
      <link
        href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,300;8..60,400;8..60,500;8..60,600&display=swap"
        rel="stylesheet"
      />
      <style>{`
        .nivora-landing {
          position: fixed;
          inset: 0;
          background: #1C1917;
          color: #FAF9F7;
          overflow: hidden;
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .particle-canvas {
          position: absolute;
          inset: 0;
          z-index: 0;
        }

        /* Ambient gradients */
        .ambient-gradient {
          position: absolute;
          border-radius: 50%;
          filter: blur(120px);
          pointer-events: none;
          opacity: 0.5;
        }
        .gradient-1 {
          width: 600px;
          height: 600px;
          background: radial-gradient(circle, rgba(0, 229, 255, 0.3) 0%, transparent 70%);
          top: -200px;
          left: -200px;
          animation: float1 15s ease-in-out infinite;
        }
        .gradient-2 {
          width: 500px;
          height: 500px;
          background: radial-gradient(circle, rgba(127, 0, 255, 0.25) 0%, transparent 70%);
          bottom: -150px;
          right: -150px;
          animation: float2 18s ease-in-out infinite;
        }
        .gradient-3 {
          width: 400px;
          height: 400px;
          background: radial-gradient(circle, rgba(0, 191, 255, 0.2) 0%, transparent 70%);
          top: 50%;
          left: 60%;
          animation: float3 20s ease-in-out infinite;
        }

        @keyframes float1 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(50px, 30px) scale(1.1); }
          66% { transform: translate(-30px, 50px) scale(0.95); }
        }
        @keyframes float2 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(-40px, -30px) scale(1.05); }
          66% { transform: translate(30px, -40px) scale(0.9); }
        }
        @keyframes float3 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          50% { transform: translate(-60px, 40px) scale(1.15); }
        }

        /* Top navigation */
        .nav-bar {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 24px 48px;
          z-index: 20;
        }
        .nav-logo {
          display: flex;
          align-items: center;
          gap: 14px;
        }
        .nav-logo-img {
          width: 40px;
          height: 40px;
          border-radius: 10px;
          object-fit: cover;
        }
        .nav-logo-text {
          font-family: 'Source Serif 4', Georgia, serif;
          font-size: 22px;
          font-weight: 500;
          letter-spacing: 0.02em;
          color: #FAF9F7;
        }
        .nav-links {
          display: flex;
          align-items: center;
          gap: 32px;
        }
        .nav-link {
          font-size: 14px;
          font-weight: 500;
          color: rgba(250, 249, 247, 0.6);
          text-decoration: none;
          transition: color 0.2s ease;
          letter-spacing: 0.01em;
        }
        .nav-link:hover {
          color: #FAF9F7;
        }

        /* Main content */
        .main-content {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          text-align: center;
          z-index: 10;
          width: 100%;
          max-width: 800px;
          padding: 0 24px;
        }

        /* Logo container */
        .logo-container {
          position: relative;
          width: 200px;
          height: 200px;
          margin: 0 auto 48px;
        }
        .logo-glow {
          position: absolute;
          inset: -30px;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(0, 229, 255, 0.4) 0%, transparent 70%);
          z-index: 0;
        }
        .main-logo {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 160px;
          height: 160px;
          border-radius: 50%;
          object-fit: cover;
          z-index: 2;
          box-shadow: 0 0 60px rgba(0, 229, 255, 0.4), 0 0 100px rgba(127, 0, 255, 0.2);
        }
        .logo-ring {
          position: absolute;
          inset: -10px;
          border: 1px solid rgba(0, 229, 255, 0.3);
          border-radius: 50%;
          animation: pulse-ring 3s ease-out infinite;
        }
        .logo-ring-2 {
          inset: -25px;
          border-color: rgba(127, 0, 255, 0.2);
          animation-delay: 1.5s;
        }

        @keyframes pulse-ring {
          0% { transform: scale(1); opacity: 1; }
          100% { transform: scale(1.3); opacity: 0; }
        }

        /* Status badge */
        .status-badge {
          display: inline-flex;
          align-items: center;
          gap: 10px;
          padding: 10px 20px;
          background: rgba(0, 229, 255, 0.08);
          border: 1px solid rgba(0, 229, 255, 0.2);
          border-radius: 100px;
          margin-bottom: 32px;
        }
        .status-dot {
          width: 8px;
          height: 8px;
          background: #00E5FF;
          border-radius: 50%;
          animation: pulse-dot 2s ease-in-out infinite;
          box-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
        }
        @keyframes pulse-dot {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(1.2); }
        }
        .status-text {
          font-size: 12px;
          font-weight: 500;
          color: #00E5FF;
          letter-spacing: 0.1em;
          text-transform: uppercase;
        }

        /* Title */
        .hero-title {
          font-family: 'Source Serif 4', Georgia, serif;
          font-size: clamp(48px, 10vw, 96px);
          font-weight: 400;
          letter-spacing: -0.02em;
          line-height: 1.1;
          margin-bottom: 20px;
          color: #FAF9F7;
        }
        .title-gradient {
          background: linear-gradient(120deg,
            #00E5FF,
            #7F00FF,
            #00BFFF,
            #4B0082,
            #00E5FF,
            #9400D3,
            #00E5FF);
          background-size: 300% 300%;
          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;
          color: transparent;
          animation: aurora-shift 6s ease infinite;
          filter: drop-shadow(0 0 24px rgba(0, 229, 255, 0.35));
        }

        @keyframes aurora-shift {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }

        /* Subtitle with typing */
        .hero-subtitle {
          font-size: 20px;
          font-weight: 400;
          color: rgba(0, 229, 255, 0.7);
          margin-bottom: 16px;
          min-height: 30px;
          letter-spacing: 0.01em;
        }
        .cursor {
          color: #00E5FF;
          animation: blink 1s step-end infinite;
        }
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }

        /* Description */
        .hero-description {
          font-size: 16px;
          color: rgba(250, 249, 247, 0.5);
          line-height: 1.7;
          margin-bottom: 48px;
          max-width: 500px;
          margin-left: auto;
          margin-right: auto;
        }
        .highlight {
          color: #00E5FF;
          font-weight: 500;
        }

        /* Capabilities */
        .capabilities {
          display: flex;
          flex-wrap: wrap;
          justify-content: center;
          gap: 12px;
          margin-bottom: 48px;
        }
        .capability {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 20px;
          background: rgba(250, 249, 247, 0.03);
          border: 1px solid rgba(250, 249, 247, 0.08);
          border-radius: 100px;
          font-size: 14px;
          color: rgba(250, 249, 247, 0.7);
          transition: all 0.3s ease;
        }
        .capability:hover {
          background: rgba(0, 229, 255, 0.1);
          border-color: rgba(0, 229, 255, 0.3);
          transform: translateY(-2px);
        }

        /* CTA Button - Aurora style */
        .cta-button {
          display: inline-flex;
          align-items: center;
          gap: 12px;
          padding: 16px 32px;
          background: linear-gradient(135deg, #00BFFF 0%, #1E90FF 50%, #00CED1 100%);
          border: none;
          border-radius: 100px;
          font-family: 'Inter', sans-serif;
          font-size: 15px;
          font-weight: 500;
          color: white;
          cursor: pointer;
          transition: all 0.3s ease;
          box-shadow: 0 4px 20px rgba(0, 191, 255, 0.3), 0 0 40px rgba(30, 144, 255, 0.15);
        }
        .cta-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 30px rgba(0, 191, 255, 0.4), 0 0 60px rgba(30, 144, 255, 0.25);
        }
        .cta-button:active {
          transform: translateY(0);
        }
        .cta-icon {
          width: 18px;
          height: 18px;
        }

        /* Marquee section */
        .marquee-section {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          padding: 24px 0;
          border-top: 1px solid rgba(250, 249, 247, 0.05);
          z-index: 10;
        }
        .marquee-label {
          text-align: center;
          font-size: 11px;
          color: rgba(250, 249, 247, 0.3);
          letter-spacing: 0.15em;
          text-transform: uppercase;
          margin-bottom: 20px;
        }
        .marquee-wrapper {
          overflow: hidden;
          -webkit-mask-image: linear-gradient(to right, transparent 0%, black 10%, black 90%, transparent 100%);
          mask-image: linear-gradient(to right, transparent 0%, black 10%, black 90%, transparent 100%);
        }
        .marquee-track {
          display: flex;
          width: max-content;
          animation: scroll-marquee 40s linear infinite;
        }
        .marquee-track:hover {
          animation-play-state: paused;
        }
        .marquee-item {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0 40px;
        }
        .marquee-logo {
          height: 28px;
          width: auto;
          max-width: 100px;
          opacity: 0.4;
          filter: brightness(0) invert(1);
          transition: all 0.3s ease;
        }
        .marquee-logo:hover {
          opacity: 1;
          filter: none;
        }

        @keyframes scroll-marquee {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }

        /* Mobile responsive */
        @media (max-width: 768px) {
          .nav-bar {
            padding: 16px 24px;
          }
          .nav-links {
            display: none;
          }
          .logo-container {
            width: 160px;
            height: 160px;
            margin-bottom: 32px;
          }
          .main-logo {
            width: 120px;
            height: 120px;
          }
          .hero-title {
            font-size: clamp(36px, 12vw, 64px);
          }
          .hero-subtitle {
            font-size: 16px;
          }
          .capability {
            padding: 10px 16px;
            font-size: 12px;
          }
          .cta-button {
            padding: 14px 28px;
            font-size: 14px;
          }
        }
      `}</style>

      {/* Background */}
      <ParticleField />
      <div className="ambient-gradient gradient-1" />
      <div className="ambient-gradient gradient-2" />
      <div className="ambient-gradient gradient-3" />

      {/* Navigation */}
      <motion.nav
        className="nav-bar"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <div className="nav-logo">
          <img
            src="/WhatsApp Image 2026-03-29 at 19.06.46.jpeg"
            alt="Nivora"
            className="nav-logo-img"
          />
          <span className="nav-logo-text">Nivora</span>
        </div>
        <div className="nav-links">
          <a href="#" className="nav-link">Features</a>
          <a href="#" className="nav-link">About</a>
          <a href="#" className="nav-link">Contact</a>
        </div>
      </motion.nav>

      {/* Main Content */}
      <div className="main-content">
        <AnimatedLogo />

        <motion.div
          className="status-badge"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          <div className="status-dot" />
          <span className="status-text">Personal AI Assistant</span>
        </motion.div>

        <motion.h1
          className="hero-title"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          Meet <span className="title-gradient">Nivora</span>
        </motion.h1>

        <motion.p
          className="hero-subtitle"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 1.0 }}
        >
          {typedText}<span className="cursor">|</span>
        </motion.p>

        <motion.p
          className="hero-description"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.2 }}
        >
          Talk naturally. Control your computer. Manage your life.<br />
          <span className="highlight">Think Jarvis, powered by AI.</span>
        </motion.p>

        <motion.div
          className="capabilities"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.4 }}
        >
          {CAPABILITIES.map((cap, i) => (
            <motion.div
              key={cap.title}
              className="capability"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: 1.4 + i * 0.1 }}
              whileHover={{ scale: 1.05 }}
            >
              <span>{cap.icon}</span>
              <span>{cap.title}</span>
            </motion.div>
          ))}
        </motion.div>

        <motion.button
          className="cta-button"
          onClick={onStartCall}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.8 }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <svg className="cta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            <line x1="12" y1="19" x2="12" y2="23" />
            <line x1="8" y1="23" x2="16" y2="23" />
          </svg>
          Try Demo
        </motion.button>
      </div>

      {/* Bottom Marquee with Logos */}
      <motion.div
        className="marquee-section"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 2.0 }}
      >
        <div className="marquee-label">Powered by Leading AI Models</div>
        <div className="marquee-wrapper">
          <div className="marquee-track">
            {[...AI_MODEL_LOGOS, ...AI_MODEL_LOGOS].map((model, i) => (
              <div key={i} className="marquee-item">
                <img
                  src={model.logo}
                  alt={model.name}
                  className="marquee-logo"
                />
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default LandingPage;
