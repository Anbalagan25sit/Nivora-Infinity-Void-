'use client';

import { ArrowRight, Github } from 'lucide-react';
import { motion } from 'motion/react';

export function HeroSection() {
  return (
    <section className="relative flex min-h-screen items-center justify-center overflow-hidden bg-black">
      {/* Animated Gradient Orb */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="animate-pulse-slow absolute top-1/2 left-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-gradient-to-r from-cyan-600/20 via-blue-600/20 to-purple-600/20 blur-[120px]" />
        <div className="animate-float absolute top-1/3 left-1/3 h-[400px] w-[400px] rounded-full bg-gradient-to-br from-cyan-500/10 to-blue-500/10 blur-[100px]" />
      </div>

      {/* Noise Texture Overlay */}
      <div className="pointer-events-none absolute inset-0 opacity-[0.015] mix-blend-overlay">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage:
              "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' /%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' /%3E%3C/svg%3E\")",
          }}
        />
      </div>

      <div className="relative z-10 container mx-auto px-6 py-20">
        <div className="mx-auto max-w-5xl text-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="mb-8 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 backdrop-blur-sm"
          >
            <span className="text-xs font-medium text-purple-400">Built with</span>
            <span className="text-xs text-gray-300">LiveKit + n8n + AWS Nova Pro</span>
          </motion.div>

          {/* Main Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="mb-6 text-6xl font-bold tracking-tight md:text-7xl lg:text-8xl"
          >
            <span className="bg-gradient-to-r from-white via-white to-gray-400 bg-clip-text text-transparent">
              Your AI agent.
            </span>
            <br />
            <span className="bg-gradient-to-r from-white via-gray-200 to-gray-500 bg-clip-text text-transparent">
              Your machine.
            </span>
            <br />
            <span className="bg-gradient-to-r from-purple-400 via-purple-300 to-cyan-400 bg-clip-text text-transparent">
              Your rules.
            </span>
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="mx-auto mb-10 max-w-3xl text-lg leading-relaxed text-gray-400 md:text-xl"
          >
            Nivora is an open-source desktop AI agent with voice control, browser automation, and
            workflow intelligence — running locally by default.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="mb-16 flex flex-col items-center justify-center gap-4 sm:flex-row"
          >
            <a
              href="/playground"
              className="group relative overflow-hidden rounded-full bg-gradient-to-r from-purple-600 to-purple-500 px-8 py-4 text-lg font-semibold text-white transition-all hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/50"
            >
              <span className="relative z-10 flex items-center gap-2">
                Try Live Demo
                <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-purple-600 opacity-0 transition-opacity group-hover:opacity-100" />
            </a>

            <a
              href="https://github.com/nivora/nivora"
              target="_blank"
              rel="noopener noreferrer"
              className="group flex items-center gap-2 rounded-full border-2 border-white/20 px-8 py-4 text-lg font-semibold text-white transition-all hover:border-white/40 hover:bg-white/5"
            >
              <Github className="h-5 w-5" />
              View on GitHub
            </a>
          </motion.div>

          {/* Floating Code Snippet */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            className="inline-flex items-center gap-3 rounded-2xl border border-white/10 bg-black/40 px-6 py-4 shadow-2xl backdrop-blur-xl"
          >
            <div className="flex gap-2">
              <div className="h-3 w-3 rounded-full bg-red-500" />
              <div className="h-3 w-3 rounded-full bg-yellow-500" />
              <div className="h-3 w-3 rounded-full bg-green-500" />
            </div>
            <code className="font-mono text-sm text-gray-300 md:text-base">
              <span className="text-purple-400">python</span>{' '}
              <span className="text-cyan-400">agent/main.py</span>{' '}
              <span className="text-green-400">dev</span>
            </code>
            <div className="animate-blink h-5 w-2 bg-purple-400" />
          </motion.div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 1.2 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
      >
        <div className="flex h-10 w-6 items-start justify-center rounded-full border-2 border-white/20 p-2">
          <div className="animate-scroll h-3 w-1.5 rounded-full bg-white/60" />
        </div>
      </motion.div>
    </section>
  );
}
