'use client';

import { motion } from 'motion/react';
import { Code, Globe, Cloud, Phone, BarChart3 } from 'lucide-react';

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
    <section className="relative py-32 bg-black overflow-hidden">
      {/* 3D Grid Background */}
      <div className="absolute inset-0 opacity-30">
        <svg className="w-full h-full" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid slice">
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
          <rect width="100%" height="100%" fill="url(#grid)" transform="perspective(500px) rotateX(60deg)" />
        </svg>
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="grid lg:grid-cols-2 gap-20 items-center">
          {/* Left Content */}
          <div>
            <div className="inline-block px-4 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono mb-6">
              DEVELOPER PLATFORM
            </div>

            <h2 className="text-5xl font-bold mb-6">
              <span className="text-white">The </span>
              <span className="text-cyan-400">complete</span>
              <span className="text-white"> stack for</span>
              <br />
              <span className="text-white">Voice AI</span>
            </h2>

            <div className="space-y-5 mb-10">
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
                    <div className="w-10 h-10 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0 mt-1">
                      <Icon className="w-5 h-5 text-cyan-400" />
                    </div>
                    <p className="text-gray-300 text-lg leading-relaxed">{feature.title}</p>
                  </motion.div>
                );
              })}
            </div>

            <button className="px-6 py-3 rounded-lg bg-white/5 border border-white/10 text-white hover:bg-white/10 hover:border-white/30 transition-all">
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
              <div className="w-40 h-32 bg-gradient-to-br from-gray-900 to-black border border-white/10 rounded-lg shadow-2xl p-4">
                <div className="text-xs text-gray-500 mb-2">LiveKit Cloud</div>
                <div className="text-sm text-white font-medium">Real-time Infrastructure</div>
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
              <div className="w-40 h-32 bg-gradient-to-br from-cyan-900/50 to-blue-900/50 border border-cyan-500/30 rounded-lg shadow-2xl p-4">
                <div className="text-xs text-cyan-400 mb-2">Media Server</div>
                <div className="text-sm text-white font-medium">WebRTC Gateway</div>
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
              <div className="w-40 h-32 bg-gradient-to-br from-purple-900/50 to-pink-900/50 border border-purple-500/30 rounded-lg shadow-2xl p-4">
                <div className="text-xs text-purple-400 mb-2">Agent Server</div>
                <div className="text-sm text-white font-medium">Business Logic</div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5 }}
              className="absolute bottom-40 right-10"
              style={{ transform: 'rotateX(20deg) rotateY(-20deg) rotateZ(5deg)' }}
            >
              <div className="w-40 h-32 bg-gradient-to-br from-gray-900 to-black border border-white/10 rounded-lg shadow-2xl p-4">
                <div className="text-xs text-gray-500 mb-2">SDKs</div>
                <div className="text-sm text-white font-medium">Client Libraries</div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.6 }}
              className="absolute bottom-20 right-40"
              style={{ transform: 'rotateX(20deg) rotateY(-20deg) rotateZ(5deg)' }}
            >
              <div className="w-40 h-32 bg-gradient-to-br from-green-900/50 to-emerald-900/50 border border-green-500/30 rounded-lg shadow-2xl p-4">
                <div className="text-xs text-green-400 mb-2">AI Models</div>
                <div className="text-sm text-white font-medium">STT • LLM • TTS</div>
              </div>
            </motion.div>

            {/* Connecting Lines */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none">
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
            <div className="absolute bottom-0 right-0 text-right">
              <div className="text-sm text-gray-500 uppercase tracking-widest">Global Edge</div>
              <div className="text-sm text-gray-500 uppercase tracking-widest">Network</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
