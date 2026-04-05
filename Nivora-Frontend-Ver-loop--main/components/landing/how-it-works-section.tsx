'use client';

import { motion } from 'motion/react';

const steps = [
  {
    number: '1',
    title: 'User speaks to agent via app, browser, or phone call',
  },
  {
    number: '2',
    title: 'User speech is streamed from device to agent',
    description:
      'Voice, video, and text data travel via WebRTC through LiveKit\'s global edge network with less than 100ms latency.',
  },
  {
    number: '3',
    title: 'Agent receives user speech and runs your custom business logic',
  },
  {
    number: '4',
    title: 'Agent responds back to the user',
  },
];

export function HowItWorksSection() {
  return (
    <section className="relative py-32 bg-gradient-to-b from-black to-gray-950 overflow-hidden">
      {/* Background Grid */}
      <div className="absolute inset-0 opacity-10">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)
            `,
            backgroundSize: '30px 30px',
          }}
        />
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="grid lg:grid-cols-2 gap-20 items-center">
          {/* Left - Steps */}
          <div>
            <h2 className="text-5xl font-bold mb-16">
              <span className="text-cyan-400">How</span>
              <span className="text-white"> it works</span>
            </h2>

            <div className="space-y-8">
              {steps.map((step, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -30 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className="flex gap-6"
                >
                  {/* Number Badge */}
                  <div className="flex-shrink-0 w-10 h-10 rounded-full border-2 border-white/20 flex items-center justify-center text-white font-bold">
                    {step.number}
                  </div>

                  {/* Content */}
                  <div>
                    <h3 className="text-white text-lg font-semibold mb-2">{step.title}</h3>
                    {step.description && (
                      <p className="text-gray-400 text-sm leading-relaxed">{step.description}</p>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Right - 3D Isometric Illustration */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="relative h-[600px]"
          >
            {/* Device Screens */}
            <div
              className="absolute top-20 left-20 w-48 h-64 bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg border border-white/10 shadow-2xl"
              style={{ transform: 'rotateX(20deg) rotateY(-20deg)' }}
            >
              <div className="p-4">
                <div className="w-full h-3 bg-white/10 rounded mb-2" />
                <div className="w-3/4 h-3 bg-white/10 rounded mb-4" />
                <div className="grid grid-cols-2 gap-2">
                  {[...Array(6)].map((_, i) => (
                    <div key={i} className="h-8 bg-white/5 rounded" />
                  ))}
                </div>
              </div>
            </div>

            {/* Network Node */}
            <motion.div
              animate={{
                scale: [1, 1.1, 1],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
              className="absolute top-40 right-40 w-32 h-32 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-2xl border border-cyan-500/30 shadow-2xl backdrop-blur-xl"
              style={{ transform: 'rotateX(20deg) rotateY(-20deg)' }}
            >
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-xs text-cyan-400 font-mono mb-1">GLOBAL EDGE</div>
                  <div className="text-xs text-white font-mono">NETWORK</div>
                </div>
              </div>
            </motion.div>

            {/* Server Card */}
            <div
              className="absolute bottom-40 right-20 w-56 h-40 bg-gradient-to-br from-gray-900 to-black rounded-xl border border-white/10 shadow-2xl"
              style={{ transform: 'rotateX(20deg) rotateY(-20deg)' }}
            >
              <div className="p-4">
                <div className="text-xs text-gray-500 mb-3">AGENT FRAMEWORK</div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                    <div className="text-xs text-gray-400">Noise cancellation</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" />
                    <div className="text-xs text-gray-400">STT</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-purple-500 rounded-full animate-pulse" />
                    <div className="text-xs text-gray-400">LLM</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-pink-500 rounded-full animate-pulse" />
                    <div className="text-xs text-gray-400">TTS</div>
                  </div>
                </div>
              </div>
            </div>

            {/* SDK Indicators */}
            <div
              className="absolute bottom-20 left-40 w-32 h-24 bg-gradient-to-br from-purple-900/50 to-pink-900/50 rounded-lg border border-purple-500/30 shadow-2xl"
              style={{ transform: 'rotateX(20deg) rotateY(-20deg)' }}
            >
              <div className="p-3">
                <div className="text-xs text-purple-400 mb-2">CLIENT</div>
                <div className="text-xs text-white font-mono">SDKs</div>
              </div>
            </div>

            {/* Animated Connection Lines */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none">
              <motion.path
                d="M 150 200 Q 300 250 400 280"
                stroke="rgba(6, 182, 212, 0.4)"
                strokeWidth="2"
                fill="none"
                strokeDasharray="5,5"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              />
              <motion.path
                d="M 450 320 Q 480 380 420 440"
                stroke="rgba(168, 85, 247, 0.4)"
                strokeWidth="2"
                fill="none"
                strokeDasharray="5,5"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 2, delay: 0.5, repeat: Infinity, ease: 'linear' }}
              />
            </svg>

            {/* Label */}
            <div className="absolute bottom-0 right-0 text-right">
              <div className="text-sm text-gray-600 uppercase tracking-wider">Custom Business</div>
              <div className="text-sm text-gray-600 uppercase tracking-wider">Logic</div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
