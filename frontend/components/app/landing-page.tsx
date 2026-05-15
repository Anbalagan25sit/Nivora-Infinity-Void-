'use client';

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';

// =============================================================================
// NIVORA CINEMATIC VOID - Immersive Voice Playground
// =============================================================================

// =============================================================================
// COSMIC BACKGROUND - Ethereal particle field with depth
// =============================================================================

function CosmicBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId: number;
    let time = 0;

    interface Star {
      x: number;
      y: number;
      z: number;
      size: number;
      speed: number;
    }

    let stars: Star[] = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initStars();
    };

    const initStars = () => {
      stars = [];
      const count = Math.min(200, Math.floor((canvas.width * canvas.height) / 8000));
      for (let i = 0; i < count; i++) {
        stars.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          z: Math.random() * 3,
          size: Math.random() * 1.5 + 0.5,
          speed: Math.random() * 0.3 + 0.1,
        });
      }
    };

    const animate = () => {
      time += 0.005;

      // Clear with subtle fade for trail effect
      ctx.fillStyle = 'rgba(5, 5, 8, 0.15)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw stars with parallax depth
      stars.forEach((star) => {
        const parallaxX = Math.sin(time * star.speed) * (star.z * 2);
        const parallaxY = Math.cos(time * star.speed * 0.7) * (star.z * 1.5);

        const x = star.x + parallaxX;
        const y = star.y + parallaxY;

        // Pulsing glow
        const pulse = Math.sin(time * 2 + star.x) * 0.3 + 0.7;
        const opacity = (0.3 + star.z * 0.2) * pulse;

        ctx.beginPath();
        ctx.arc(x, y, star.size * (0.8 + star.z * 0.3), 0, Math.PI * 2);
        ctx.fillStyle = `rgba(180, 200, 255, ${opacity})`;
        ctx.fill();

        // Subtle glow halo
        if (star.z > 2) {
          ctx.beginPath();
          ctx.arc(x, y, star.size * 3, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(120, 160, 255, ${opacity * 0.1})`;
          ctx.fill();
        }
      });

      // Central nebula glow
      const gradient = ctx.createRadialGradient(
        canvas.width / 2,
        canvas.height / 2,
        0,
        canvas.width / 2,
        canvas.height / 2,
        canvas.width * 0.5
      );
      gradient.addColorStop(0, 'rgba(80, 40, 120, 0.03)');
      gradient.addColorStop(0.3, 'rgba(40, 80, 120, 0.02)');
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

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

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 z-0"
      style={{ background: 'linear-gradient(180deg, #050508 0%, #0a0a12 50%, #080810 100%)' }}
    />
  );
}

// =============================================================================
// VOICE ORB - Central audio-reactive visualization
// =============================================================================

function VoiceOrb({ isHovered, onClick }: { isHovered: boolean; onClick: () => void }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId: number;
    let time = 0;

    const size = 400;
    canvas.width = size;
    canvas.height = size;

    const animate = () => {
      time += 0.02;
      ctx.clearRect(0, 0, size, size);

      const centerX = size / 2;
      const centerY = size / 2;
      const baseRadius = isHovered ? 95 : 85;

      // Outer ethereal rings
      for (let ring = 4; ring >= 0; ring--) {
        const ringRadius = baseRadius + ring * 25 + Math.sin(time + ring) * 5;
        const opacity = (0.08 - ring * 0.015) * (isHovered ? 1.3 : 1);

        ctx.beginPath();
        ctx.arc(centerX, centerY, ringRadius, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(100, 180, 255, ${opacity})`;
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      // Main orb glow layers
      const glowLayers = [
        { radius: baseRadius + 40, color: 'rgba(60, 100, 180, 0.05)' },
        { radius: baseRadius + 25, color: 'rgba(80, 140, 220, 0.08)' },
        { radius: baseRadius + 10, color: 'rgba(100, 160, 240, 0.12)' },
      ];

      glowLayers.forEach((layer) => {
        const gradient = ctx.createRadialGradient(
          centerX,
          centerY,
          0,
          centerX,
          centerY,
          layer.radius
        );
        gradient.addColorStop(0.6, layer.color);
        gradient.addColorStop(1, 'transparent');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, size, size);
      });

      // Core orb with gradient
      const coreGradient = ctx.createRadialGradient(
        centerX - 20,
        centerY - 20,
        0,
        centerX,
        centerY,
        baseRadius
      );
      coreGradient.addColorStop(0, 'rgba(180, 210, 255, 0.95)');
      coreGradient.addColorStop(0.4, 'rgba(100, 160, 240, 0.85)');
      coreGradient.addColorStop(0.8, 'rgba(60, 120, 200, 0.75)');
      coreGradient.addColorStop(1, 'rgba(40, 80, 160, 0.6)');

      ctx.beginPath();
      ctx.arc(centerX, centerY, baseRadius, 0, Math.PI * 2);
      ctx.fillStyle = coreGradient;
      ctx.fill();

      // Inner luminance
      const innerGlow = ctx.createRadialGradient(
        centerX - 15,
        centerY - 15,
        0,
        centerX,
        centerY,
        baseRadius * 0.6
      );
      innerGlow.addColorStop(0, 'rgba(255, 255, 255, 0.4)');
      innerGlow.addColorStop(1, 'transparent');
      ctx.fillStyle = innerGlow;
      ctx.fillRect(0, 0, size, size);

      // Animated wave pattern inside orb
      ctx.save();
      ctx.beginPath();
      ctx.arc(centerX, centerY, baseRadius - 2, 0, Math.PI * 2);
      ctx.clip();

      for (let i = 0; i < 6; i++) {
        const waveY = centerY + (i - 2.5) * 18;
        ctx.beginPath();
        ctx.moveTo(centerX - baseRadius, waveY);

        for (let x = -baseRadius; x <= baseRadius; x += 2) {
          const amplitude = 8 + Math.sin(time + i * 0.5) * 4;
          const frequency = 0.03 + Math.cos(time * 0.5) * 0.01;
          const y = waveY + Math.sin(x * frequency + time * 2 + i) * amplitude;
          ctx.lineTo(centerX + x, y);
        }

        const opacity = 0.15 + (isHovered ? 0.1 : 0);
        ctx.strokeStyle = `rgba(255, 255, 255, ${opacity})`;
        ctx.lineWidth = 2;
        ctx.stroke();
      }
      ctx.restore();

      // Orbiting particles
      for (let i = 0; i < 8; i++) {
        const angle = time * 0.5 + i * (Math.PI / 4);
        const orbitRadius = baseRadius + 55 + Math.sin(time * 2 + i) * 10;
        const px = centerX + Math.cos(angle) * orbitRadius;
        const py = centerY + Math.sin(angle) * orbitRadius;
        const particleSize = 2 + Math.sin(time + i) * 1;

        ctx.beginPath();
        ctx.arc(px, py, particleSize, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(150, 200, 255, ${0.6 + Math.sin(time + i) * 0.3})`;
        ctx.fill();
      }

      animationId = requestAnimationFrame(animate);
    };

    animate();

    return () => cancelAnimationFrame(animationId);
  }, [isHovered]);

  return (
    <motion.div
      className="relative cursor-pointer"
      onClick={onClick}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <canvas
        ref={canvasRef}
        className="h-[300px] w-[300px] md:h-[400px] md:w-[400px]"
        style={{ filter: 'drop-shadow(0 0 60px rgba(80, 140, 220, 0.4))' }}
      />

      {/* Center icon */}
      <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
        <motion.div animate={{ scale: isHovered ? 1.1 : 1 }} transition={{ duration: 0.3 }}>
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" className="text-white/90">
            <path
              d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"
              fill="currentColor"
              fillOpacity="0.9"
            />
            <path
              d="M19 10v2a7 7 0 0 1-14 0v-2"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
            <path d="M12 19v4M8 23h8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </motion.div>
      </div>
    </motion.div>
  );
}

// =============================================================================
// MAIN LANDING PAGE COMPONENT
// =============================================================================

export interface LandingPageProps {
  onStartCall: () => void;
}

export function LandingPage({ onStartCall }: LandingPageProps) {
  const [mounted, setMounted] = useState(false);
  const [isOrbHovered, setIsOrbHovered] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleOrbClick = useCallback(() => {
    onStartCall();
  }, [onStartCall]);

  if (!mounted) return null;

  return (
    <div className="fixed inset-0 overflow-hidden bg-[#050508]">
      {/* Google Fonts - Editorial Typography */}
      <link
        href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600&family=Outfit:wght@200;300;400;500;600&display=swap"
        rel="stylesheet"
      />

      <style>{`
        .nivora-playground {
          font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .editorial-title {
          font-family: 'Cormorant Garamond', Georgia, serif;
          font-weight: 300;
          letter-spacing: -0.03em;
        }

        .text-gradient-ethereal {
          background: linear-gradient(
            135deg,
            rgba(180, 210, 255, 1) 0%,
            rgba(140, 180, 255, 1) 25%,
            rgba(200, 220, 255, 1) 50%,
            rgba(160, 190, 255, 1) 75%,
            rgba(180, 210, 255, 1) 100%
          );
          background-size: 200% 200%;
          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;
          animation: ethereal-shift 8s ease-in-out infinite;
        }

        @keyframes ethereal-shift {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }

        .capability-pill {
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.06);
          backdrop-filter: blur(20px);
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .capability-pill:hover {
          background: rgba(100, 160, 240, 0.08);
          border-color: rgba(100, 160, 240, 0.2);
          transform: translateY(-2px);
        }

        .hint-text {
          opacity: 0;
          animation: fadeInUp 0.8s ease forwards;
          animation-delay: 2s;
        }

        @keyframes fadeInUp {
          to {
            opacity: 1;
            transform: translateY(0);
          }
          from {
            opacity: 0;
            transform: translateY(10px);
          }
        }

        .ambient-line {
          position: absolute;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(100, 160, 240, 0.15), transparent);
        }

        .creator-badge {
          position: relative;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 255, 255, 0.05);
          border-radius: 100px;
          backdrop-filter: blur(10px);
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .creator-badge:hover {
          background: rgba(100, 160, 240, 0.06);
          border-color: rgba(100, 160, 240, 0.15);
          transform: translateY(-1px);
        }

        .creator-badge::before {
          content: '';
          position: absolute;
          inset: -1px;
          border-radius: inherit;
          padding: 1px;
          background: linear-gradient(
            135deg,
            rgba(100, 160, 240, 0.2) 0%,
            transparent 50%,
            rgba(140, 180, 255, 0.2) 100%
          );
          -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
          mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
          -webkit-mask-composite: xor;
          mask-composite: exclude;
          opacity: 0;
          transition: opacity 0.4s ease;
        }

        .creator-badge:hover::before {
          opacity: 1;
        }

        .creator-name {
          background: linear-gradient(
            90deg,
            rgba(180, 210, 255, 0.9) 0%,
            rgba(140, 180, 255, 1) 50%,
            rgba(180, 210, 255, 0.9) 100%
          );
          background-size: 200% 100%;
          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;
          animation: name-shimmer 4s ease-in-out infinite;
        }

        @keyframes name-shimmer {
          0%, 100% { background-position: -100% 0; }
          50% { background-position: 100% 0; }
        }

        .creator-dot {
          width: 4px;
          height: 4px;
          background: rgba(100, 160, 240, 0.6);
          border-radius: 50%;
          animation: dot-pulse 2s ease-in-out infinite;
        }

        @keyframes dot-pulse {
          0%, 100% { opacity: 0.4; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.2); }
        }
      `}</style>

      <CosmicBackground />

      {/* Subtle ambient lines */}
      <div className="ambient-line top-[20%] right-0 left-0" />
      <div className="ambient-line top-[80%] right-0 left-0" />

      {/* Main content container */}
      <div className="nivora-playground relative z-10 flex min-h-screen flex-col items-center justify-center px-6">
        {/* Top branding - minimal */}
        <motion.div
          className="fixed top-8 left-8 flex items-center gap-3"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/10 bg-gradient-to-br from-blue-400/20 to-indigo-500/20">
            <span className="text-sm font-medium text-white/80">N</span>
          </div>
          <span className="text-sm font-light tracking-wider text-white/40">NIVORA</span>
        </motion.div>

        {/* Central content */}
        <div className="flex flex-col items-center text-center">
          {/* Title */}
          <motion.h1
            className="editorial-title text-gradient-ethereal mb-4 text-5xl md:text-7xl lg:text-8xl"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.2 }}
          >
            Voice Playground
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            className="mb-16 max-w-md text-lg font-extralight tracking-wide text-white/30 md:text-xl"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            Your AI companion awaits
          </motion.p>

          {/* Voice Orb */}
          <motion.div
            className="relative mb-16"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.8, ease: [0.16, 1, 0.3, 1] }}
            onMouseEnter={() => setIsOrbHovered(true)}
            onMouseLeave={() => setIsOrbHovered(false)}
          >
            <VoiceOrb isHovered={isOrbHovered} onClick={handleOrbClick} />
          </motion.div>

          {/* Hint text */}
          <motion.p
            className="hint-text text-sm font-light tracking-widest text-white/20 uppercase"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 1.5 }}
          >
            Click the orb to begin
          </motion.p>

          {/* Capabilities */}
          <motion.div
            className="mt-12 flex max-w-2xl flex-wrap justify-center gap-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 1.8 }}
          >
            {[
              { icon: '🎙️', label: 'Voice Control' },
              { icon: '🎵', label: 'Spotify' },
              { icon: '🌐', label: 'Web Search' },
              { icon: '📧', label: 'Email' },
              { icon: '📊', label: 'Sheets' },
              { icon: '💻', label: 'System' },
            ].map((cap, i) => (
              <motion.div
                key={cap.label}
                className="capability-pill flex items-center gap-2 rounded-full px-4 py-2"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 1.8 + i * 0.1 }}
              >
                <span className="text-sm">{cap.icon}</span>
                <span className="text-xs font-light tracking-wide text-white/50">{cap.label}</span>
              </motion.div>
            ))}
          </motion.div>
        </div>

        {/* Bottom tagline */}
        <motion.div
          className="fixed right-0 bottom-8 left-0 flex flex-col items-center gap-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 2.2 }}
        >
          {/* Creator Badge */}
          <motion.div
            className="creator-badge"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 2.4 }}
            whileHover={{ scale: 1.02 }}
          >
            <span className="text-xs font-light tracking-wide text-white/30">Nivora</span>
            <span className="creator-dot" />
            <span className="text-xs font-light text-white/40">built by</span>
            <span className="creator-name text-xs font-medium tracking-wide">Anbalagan</span>
          </motion.div>

          <p className="text-xs font-light tracking-[0.3em] text-white/15 uppercase">
            Think Jarvis, powered by AI
          </p>
        </motion.div>
      </div>
    </div>
  );
}

export default LandingPage;
