'use client';

import { BarChart3, Cloud, Code, Globe, Phone } from 'lucide-react';
import { motion } from 'motion/react';

const features = [
  {
    icon: Code,
    title: 'Open source framework to build and test agents',
  },
  {
    icon: Globe,
    title: 'Inference gateway to access TTS, LLM, and STT models',
  },
  {
    icon: Cloud,
    title: 'Cloud platform for deploying and scaling agents',
  },
  {
    icon: Phone,
    title: 'Phone numbers and SIP integrations for telephony',
  },
  {
    icon: BarChart3,
    title: 'Full-stack observability for every agent session',
  },
];

export function DeveloperPlatformSection() {
  return (
    <section className="relative overflow-hidden bg-black py-32">
      {/* 3D Grid Background */}
      <div className="absolute inset-0 opacity-30">
        <svg className="h-full w-full" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid slice">
          <defs>
            <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
              <path
                d="M 50 0 L 0 0 0 50"
                fill="none"
                stroke="rgba(255,255,255,0.1)"
                strokeWidth="0.5"
              />
            </pattern>
          </defs>
          <rect
            width="100%"
            height="100%"
            fill="url(#grid)"
            transform="perspective(500px) rotateX(60deg)"
          />
        </svg>
      </div>

      <div className="relative z-10 container mx-auto px-6">
        <div className="grid items-center gap-20 lg:grid-cols-2">
          {/* Left Content */}
          <div>
            <div className="mb-6 inline-block rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1 font-mono text-xs text-cyan-400">
              DEVELOPER PLATFORM
            </div>

            <h2 className="mb-6 text-5xl font-bold">
              <span className="text-white">The </span>
              <span className="text-cyan-400">complete</span>
              <span className="text-white"> stack for</span>
              <br />
              <span className="text-white">Voice AI</span>
            </h2>

            <div className="mb-10 space-y-5">
              {features.map((feature, i) => {
                const Icon = feature.icon;
                return (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1 }}
                    className="flex items-start gap-4"
                  >
                    <div className="mt-1 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg border border-white/10 bg-white/5">
                      <Icon className="h-5 w-5 text-cyan-400" />
                    </div>
                    <p className="text-lg leading-relaxed text-gray-300">{feature.title}</p>
                  </motion.div>
                );
              })}
            </div>

            <button className="rounded-lg border border-white/10 bg-white/5 px-6 py-3 text-white transition-all hover:border-white/30 hover:bg-white/10">
              Explore the LiveKit Cloud platform
            </button>
          </div>

          {/* Right - 3D Tech Stack Visualization */}
          <div className="relative h-[600px]">
            {/* Isometric Cards */}
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="absolute top-20 right-40"
              style={{ transform: 'rotateX(20deg) rotateY(-20deg) rotateZ(5deg)' }}
            >
              <div className="h-32 w-40 rounded-lg border border-white/10 bg-gradient-to-br from-gray-900 to-black p-4 shadow-2xl">
                <div className="mb-2 text-xs text-gray-500">LiveKit Cloud</div>
                <div className="text-sm font-medium text-white">Real-time Infrastructure</div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="absolute top-40 right-20"
              style={{ transform: 'rotateX(20deg) rotateY(-20deg) rotateZ(5deg)' }}
            >
              <div className="h-32 w-40 rounded-lg border border-cyan-500/30 bg-gradient-to-br from-cyan-900/50 to-blue-900/50 p-4 shadow-2xl">
                <div className="mb-2 text-xs text-cyan-400">Media Server</div>
                <div className="text-sm font-medium text-white">WebRTC Gateway</div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="absolute top-60 right-60"
              style={{ transform: 'rotateX(20deg) rotateY(-20deg) rotateZ(5deg)' }}
            >
              <div className="h-32 w-40 rounded-lg border border-purple-500/30 bg-gradient-to-br from-purple-900/50 to-pink-900/50 p-4 shadow-2xl">
                <div className="mb-2 text-xs text-purple-400">Agent Server</div>
                <div className="text-sm font-medium text-white">Business Logic</div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5 }}
              className="absolute right-10 bottom-40"
              style={{ transform: 'rotateX(20deg) rotateY(-20deg) rotateZ(5deg)' }}
            >
              <div className="h-32 w-40 rounded-lg border border-white/10 bg-gradient-to-br from-gray-900 to-black p-4 shadow-2xl">
                <div className="mb-2 text-xs text-gray-500">SDKs</div>
                <div className="text-sm font-medium text-white">Client Libraries</div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.6 }}
              className="absolute right-40 bottom-20"
              style={{ transform: 'rotateX(20deg) rotateY(-20deg) rotateZ(5deg)' }}
            >
              <div className="h-32 w-40 rounded-lg border border-green-500/30 bg-gradient-to-br from-green-900/50 to-emerald-900/50 p-4 shadow-2xl">
                <div className="mb-2 text-xs text-green-400">AI Models</div>
                <div className="text-sm font-medium text-white">STT • LLM • TTS</div>
              </div>
            </motion.div>

            {/* Connecting Lines */}
            <svg className="pointer-events-none absolute inset-0 h-full w-full">
              <motion.path
                d="M 400 150 L 350 250"
                stroke="rgba(6, 182, 212, 0.3)"
                strokeWidth="2"
                fill="none"
                initial={{ pathLength: 0 }}
                whileInView={{ pathLength: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 1, delay: 0.7 }}
              />
              <motion.path
                d="M 350 250 L 250 350"
                stroke="rgba(168, 85, 247, 0.3)"
                strokeWidth="2"
                fill="none"
                initial={{ pathLength: 0 }}
                whileInView={{ pathLength: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 1, delay: 0.8 }}
              />
            </svg>

            {/* Text Labels */}
            <div className="absolute right-0 bottom-0 text-right">
              <div className="text-sm tracking-widest text-gray-500 uppercase">Global Edge</div>
              <div className="text-sm tracking-widest text-gray-500 uppercase">Network</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
