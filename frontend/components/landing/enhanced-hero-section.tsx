'use client';

import { useRef } from 'react';
import { ArrowRight, Github } from 'lucide-react';
import { motion, useScroll, useTransform } from 'motion/react';
import { ANIMATION_CONFIG, blurIn, fadeInUp, scaleIn } from '@/lib/animations';

export function EnhancedHeroSection() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end start'],
  });

  const y = useTransform(scrollYProgress, [0, 1], [0, 300]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 0.95]);

  return (
    <motion.section
      ref={containerRef}
      style={{ opacity, scale }}
      className="relative flex min-h-screen items-center justify-center overflow-hidden bg-black"
    >
      {/* Animated Gradient Orbs with Parallax */}
      <motion.div style={{ y }} className="absolute inset-0 overflow-hidden">
        {/* Primary Orb */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute top-1/2 left-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full blur-[120px]"
          style={{
            background:
              'radial-gradient(circle, rgba(6,182,212,0.4) 0%, rgba(59,130,246,0.2) 50%, transparent 100%)',
          }}
        />

        {/* Secondary Orb */}
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.2, 0.4, 0.2],
            x: [-20, 20, -20],
            y: [-20, 20, -20],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute top-1/3 left-1/3 h-[400px] w-[400px] rounded-full blur-[100px]"
          style={{
            background:
              'radial-gradient(circle, rgba(139,92,246,0.3) 0%, rgba(59,130,246,0.15) 50%, transparent 100%)',
          }}
        />

        {/* Accent Orb */}
        <motion.div
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.15, 0.3, 0.15],
          }}
          transition={{
            duration: 7,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: 1,
          }}
          className="absolute right-1/4 bottom-1/4 h-[350px] w-[350px] rounded-full blur-[90px]"
          style={{
            background: 'radial-gradient(circle, rgba(16,185,129,0.2) 0%, transparent 70%)',
          }}
        />
      </motion.div>

      {/* Grid Pattern Overlay with Animation */}
      <div className="absolute inset-0 opacity-[0.03]">
        <motion.div
          animate={{
            backgroundPosition: ['0px 0px', '50px 50px'],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'linear',
          }}
          className="absolute inset-0"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px',
          }}
        />
      </div>

      <div className="relative z-10 container mx-auto px-6 py-20">
        <div className="mx-auto max-w-5xl text-center">
          {/* Badge with shimmer effect */}
          <motion.div
            {...fadeInUp}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="mb-8 inline-block"
          >
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="relative inline-flex items-center gap-2 overflow-hidden rounded-full border border-white/10 bg-white/5 px-4 py-2 backdrop-blur-sm"
            >
              <motion.div
                animate={{
                  x: ['-100%', '200%'],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: 'linear',
                  repeatDelay: 3,
                }}
                className="absolute inset-0 w-1/3 skew-x-12 bg-gradient-to-r from-transparent via-white/10 to-transparent"
              />
              <span className="relative z-10 text-xs font-medium text-cyan-400">Built with</span>
              <span className="relative z-10 text-xs text-gray-300">
                LiveKit + n8n + AWS Nova Pro
              </span>
            </motion.div>
          </motion.div>

          {/* Main Headline with staggered reveal */}
          <div className="mb-6">
            {['Your AI agent.', 'Your machine.', 'Your rules.'].map((line, i) => (
              <motion.h1
                key={i}
                initial={{ opacity: 0, y: 30, filter: 'blur(10px)' }}
                animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                {...({
                  transition: {
                    duration: 0.8,
                    delay: 0.2 + i * 0.15,
                    ease: ANIMATION_CONFIG.easing.easeOutExpo,
                  },
                  // eslint-disable-next-line @typescript-eslint/no-explicit-any
                } as unknown as any)}
                className="text-6xl font-bold tracking-tight md:text-7xl lg:text-8xl"
              >
                <span
                  className={`bg-gradient-to-r ${
                    i === 2
                      ? 'from-cyan-400 via-blue-400 to-purple-400'
                      : 'from-white via-gray-200 to-gray-400'
                  } bg-clip-text text-transparent`}
                >
                  {line}
                </span>
              </motion.h1>
            ))}
          </div>

          {/* Subheadline with blur in */}
          <motion.p
            {...blurIn}
            transition={{ duration: 0.8, delay: 0.8 }}
            className="mx-auto mb-10 max-w-3xl text-lg leading-relaxed text-gray-400 md:text-xl"
          >
            Nivora is an open-source desktop AI agent with voice control, browser automation, and
            workflow intelligence — running locally by default.
          </motion.p>

          {/* CTA Buttons with magnetic effect */}
          <motion.div
            {...fadeInUp}
            transition={{ duration: 0.8, delay: 1 }}
            className="mb-16 flex flex-col items-center justify-center gap-4 sm:flex-row"
          >
            <motion.a
              href="/playground"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.98 }}
              className="group relative overflow-hidden rounded-full bg-gradient-to-r from-cyan-600 to-blue-600 px-8 py-4 text-lg font-semibold text-white shadow-xl shadow-cyan-500/20"
            >
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-500"
                initial={{ scale: 0, opacity: 0 }}
                whileHover={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.3 }}
              />
              <span className="relative z-10 flex items-center gap-2">
                Try Live Demo
                <motion.div
                  animate={{ x: [0, 3, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  <ArrowRight className="h-5 w-5" />
                </motion.div>
              </span>
            </motion.a>

            <motion.a
              href="https://github.com/nivora/nivora"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.05, borderColor: 'rgba(255,255,255,0.4)' }}
              whileTap={{ scale: 0.98 }}
              className="group flex items-center gap-2 rounded-full border-2 border-white/20 px-8 py-4 text-lg font-semibold text-white transition-all hover:bg-white/5"
            >
              <Github className="h-5 w-5" />
              View on GitHub
            </motion.a>
          </motion.div>

          {/* Floating Code Snippet with 3D effect */}
          <motion.div
            {...scaleIn}
            transition={{ duration: 0.8, delay: 1.2 }}
            whileHover={{
              y: -5,
              rotateX: 5,
              rotateY: 5,
              transition: { duration: 0.3 },
            }}
            style={{ transformStyle: 'preserve-3d' }}
            className="inline-flex items-center gap-3 rounded-2xl border border-white/10 bg-black/40 px-6 py-4 shadow-2xl backdrop-blur-xl"
          >
            <div className="flex gap-2">
              {['bg-red-500', 'bg-yellow-500', 'bg-green-500'].map((color, i) => (
                <motion.div
                  key={i}
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity, delay: i * 0.2 }}
                  className={`h-3 w-3 rounded-full ${color}`}
                />
              ))}
            </div>
            <code className="font-mono text-sm text-gray-300 md:text-base">
              <span className="text-cyan-400">python</span>{' '}
              <span className="text-blue-400">agent/main.py</span>{' '}
              <span className="text-green-400">dev</span>
            </code>
            <motion.div
              animate={{ opacity: [1, 0, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
              className="h-5 w-2 bg-cyan-400"
            />
          </motion.div>
        </div>
      </div>

      {/* Scroll Indicator with animation */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 1.5 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="flex h-10 w-6 items-start justify-center rounded-full border-2 border-white/20 p-2"
        >
          <motion.div
            animate={{ y: [0, 12, 0], opacity: [1, 0, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="h-3 w-1.5 rounded-full bg-white/60"
          />
        </motion.div>
      </motion.div>

      {/* Particle effect (optional decorative elements) */}
      {[...Array(5)].map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0 }}
          animate={{
            opacity: [0, 0.3, 0],
            y: [0, -100],
            x: Math.random() * 40 - 20,
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: i * 0.5,
          }}
          className="absolute bottom-0 h-1 w-1 rounded-full bg-cyan-400"
          style={{
            left: `${20 + i * 15}%`,
          }}
        />
      ))}
    </motion.section>
  );
}
