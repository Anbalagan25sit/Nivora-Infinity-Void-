'use client';

import { motion } from 'motion/react';
import { useState } from 'react';
import { Mic2, Video, Bot } from 'lucide-react';

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
  const [activeTab, setActiveTab] = useState('voice');

  return (
    <section className="relative py-32 bg-black overflow-hidden">
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

      <div className="container mx-auto px-6 relative z-10">
        {/* Tabs */}
        <div className="flex items-center gap-4 mb-20">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`group relative px-6 py-3 rounded-lg border transition-all ${
                  activeTab === tab.id
                    ? 'bg-cyan-500/10 border-cyan-500/50 text-cyan-400'
                    : 'bg-white/5 border-white/10 text-gray-400 hover:border-white/30'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Icon className="w-4 h-4" />
                  <span className="text-xs font-mono font-semibold">{tab.label}</span>
                </div>
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute inset-0 bg-cyan-500/5 rounded-lg -z-10"
                    transition={{ type: 'spring', duration: 0.5 }}
                  />
                )}
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left Content */}
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="flex items-center gap-4 mb-8">
              <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center p-2">
                <img src={content[activeTab].logo} alt="Logo" className="w-full h-full object-contain" />
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                <span className="text-white text-sm font-bold">+</span>
              </div>
              <h3 className="text-2xl font-bold text-white">{content[activeTab].title}</h3>
            </div>

            <p className="text-lg text-gray-300 mb-8 leading-relaxed">
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
              <div className="relative rounded-[3rem] bg-gradient-to-br from-gray-800 to-gray-900 p-3 shadow-2xl border-8 border-gray-950">
                {/* Screen */}
                <div className="relative rounded-[2.5rem] bg-black overflow-hidden aspect-[9/19]">
                  {/* Status Bar */}
                  <div className="absolute top-0 left-0 right-0 h-8 flex items-center justify-between px-8 text-white text-xs z-10">
                    <span>9:41</span>
                    <div className="flex gap-1">
                      <div className="w-4 h-3 border border-white/50 rounded-sm" />
                      <div className="w-4 h-3 border border-white/50 rounded-sm" />
                      <div className="w-4 h-3 border border-white/50 rounded-sm" />
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
                      className="relative w-40 h-40 rounded-full"
                      style={{
                        background: 'linear-gradient(135deg, #0ea5e9 0%, #3b82f6 50%, #8b5cf6 100%)',
                        filter: 'blur(2px)',
                      }}
                    />
                  </div>

                  {/* Text Overlay */}
                  <div className="absolute bottom-20 left-0 right-0 text-center px-8">
                    <h4 className="text-white text-2xl font-bold mb-2">Breeze</h4>
                    <p className="text-gray-400 text-sm">Animated and earnest</p>

                    {/* Dots */}
                    <div className="flex justify-center gap-2 mt-6">
                      {[...Array(9)].map((_, i) => (
                        <div
                          key={i}
                          className={`w-1.5 h-1.5 rounded-full ${
                            i === 3 ? 'bg-white' : 'bg-white/30'
                          }`}
                        />
                      ))}
                    </div>
                  </div>

                  {/* Button */}
                  <div className="absolute bottom-6 left-6 right-6">
                    <button className="w-full py-4 rounded-full bg-white text-black font-semibold text-sm">
                      Start a new chat
                    </button>
                  </div>
                </div>

                {/* Notch */}
                <div className="absolute top-3 left-1/2 -translate-x-1/2 w-32 h-7 bg-black rounded-b-3xl z-20" />
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
