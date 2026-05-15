'use client';

import { useState } from 'react';
import { Bot, Mic2, Video } from 'lucide-react';
import { motion } from 'motion/react';

const tabs = [
  { id: 'voice', label: 'VOICE AI', icon: Mic2 },
  { id: 'video', label: 'VIDEO AI', icon: Video },
  { id: 'robotics', label: 'ROBOTICS', icon: Bot },
];

const content = {
  voice: {
    logo: '/lk-logo.svg',
    title: 'LiveKit + n8n + AWS Nova',
    description:
      'Nivora built voice control on LiveKit Cloud, used by millions of users around the world every day.',
    features: [
      '🌐 Run millions of concurrent calls',
      '🔄 Automatic turn detection and interruption handling',
      '🚀 Deploy and scale agents with LiveKit Cloud',
    ],
  },
  video: {
    logo: '/lk-logo.svg',
    title: 'Video Intelligence',
    description: 'Real-time video processing powered by AWS Nova Pro vision models.',
    features: [
      '👁️ Screen understanding and context awareness',
      '📹 Multi-camera support',
      '🎥 Live video analysis and processing',
    ],
  },
  robotics: {
    logo: '/lk-logo.svg',
    title: 'Robotics Integration',
    description: 'Control physical devices and robots through voice commands.',
    features: [
      '🤖 Real-time robot control',
      '📡 IoT device integration',
      '⚡ Low-latency command processing',
    ],
  },
};

export function TabbedShowcaseSection() {
  const [activeTab, setActiveTab] = useState<keyof typeof content>('voice');

  return (
    <section className="relative overflow-hidden bg-black py-32">
      {/* Background Grid */}
      <div className="absolute inset-0 opacity-20">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px',
          }}
        />
      </div>

      <div className="relative z-10 container mx-auto px-6">
        {/* Tabs */}
        <div className="mb-20 flex items-center gap-4">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as keyof typeof content)}
                className={`group relative rounded-lg border px-6 py-3 transition-all ${
                  activeTab === tab.id
                    ? 'border-cyan-500/50 bg-cyan-500/10 text-cyan-400'
                    : 'border-white/10 bg-white/5 text-gray-400 hover:border-white/30'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4" />
                  <span className="font-mono text-xs font-semibold">{tab.label}</span>
                </div>
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute inset-0 -z-10 rounded-lg bg-cyan-500/5"
                    transition={{ type: 'spring', duration: 0.5 }}
                  />
                )}
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="grid items-center gap-16 lg:grid-cols-2">
          {/* Left Content */}
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="mb-8 flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-white/10 bg-white/5 p-2">
                <img
                  src={content[activeTab].logo}
                  alt="Logo"
                  className="h-full w-full object-contain"
                />
              </div>
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600">
                <span className="text-sm font-bold text-white">+</span>
              </div>
              <h3 className="text-2xl font-bold text-white">{content[activeTab].title}</h3>
            </div>

            <p className="mb-8 text-lg leading-relaxed text-gray-300">
              {content[activeTab].description}
            </p>

            <div className="space-y-4">
              {content[activeTab].features.map((feature, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 + 0.3 }}
                  className="flex items-center gap-3 text-gray-400"
                >
                  <span className="text-base">{feature}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Right - Phone Mockup */}
          <motion.div
            key={`phone-${activeTab}`}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="relative"
          >
            {/* Phone Frame (CSS) */}
            <div className="relative mx-auto max-w-[340px]">
              {/* Phone Bezel */}
              <div className="relative rounded-[3rem] border-8 border-gray-950 bg-gradient-to-br from-gray-800 to-gray-900 p-3 shadow-2xl">
                {/* Screen */}
                <div className="relative aspect-[9/19] overflow-hidden rounded-[2.5rem] bg-black">
                  {/* Status Bar */}
                  <div className="absolute top-0 right-0 left-0 z-10 flex h-8 items-center justify-between px-8 text-xs text-white">
                    <span>9:41</span>
                    <div className="flex gap-1">
                      <div className="h-3 w-4 rounded-sm border border-white/50" />
                      <div className="h-3 w-4 rounded-sm border border-white/50" />
                      <div className="h-3 w-4 rounded-sm border border-white/50" />
                    </div>
                  </div>

                  {/* Animated Orb */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <motion.div
                      animate={{
                        scale: [1, 1.1, 1],
                        rotate: [0, 180, 360],
                      }}
                      transition={{
                        duration: 4,
                        repeat: Infinity,
                        ease: 'easeInOut',
                      }}
                      className="relative h-40 w-40 rounded-full"
                      style={{
                        background:
                          'linear-gradient(135deg, #0ea5e9 0%, #3b82f6 50%, #8b5cf6 100%)',
                        filter: 'blur(2px)',
                      }}
                    />
                  </div>

                  {/* Text Overlay */}
                  <div className="absolute right-0 bottom-20 left-0 px-8 text-center">
                    <h4 className="mb-2 text-2xl font-bold text-white">Breeze</h4>
                    <p className="text-sm text-gray-400">Animated and earnest</p>

                    {/* Dots */}
                    <div className="mt-6 flex justify-center gap-2">
                      {[...Array(9)].map((_, i) => (
                        <div
                          key={i}
                          className={`h-1.5 w-1.5 rounded-full ${
                            i === 3 ? 'bg-white' : 'bg-white/30'
                          }`}
                        />
                      ))}
                    </div>
                  </div>

                  {/* Button */}
                  <div className="absolute right-6 bottom-6 left-6">
                    <button className="w-full rounded-full bg-white py-4 text-sm font-semibold text-black">
                      Start a new chat
                    </button>
                  </div>
                </div>

                {/* Notch */}
                <div className="absolute top-3 left-1/2 z-20 h-7 w-32 -translate-x-1/2 rounded-b-3xl bg-black" />
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
