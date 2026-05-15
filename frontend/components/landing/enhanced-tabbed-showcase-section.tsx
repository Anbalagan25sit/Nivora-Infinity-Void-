'use client';

import { useRef, useState } from 'react';
import { Bot, Mic2, Video } from 'lucide-react';
import { AnimatePresence, motion, useInView } from 'motion/react';
import { ANIMATION_CONFIG, fadeInLeft, fadeInUp } from '@/lib/animations';

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

export function EnhancedTabbedShowcaseSection() {
  const [activeTab, setActiveTab] = useState<keyof typeof content>('voice');
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.3 });

  return (
    <section ref={ref} className="relative overflow-hidden bg-black py-32">
      {/* Animated Background Grid */}
      <div className="absolute inset-0 opacity-20">
        <motion.div
          animate={{
            backgroundPosition: ['0px 0px', '100px 100px'],
          }}
          transition={{
            duration: 30,
            repeat: Infinity,
            ease: 'linear',
          }}
          className="absolute inset-0"
          style={{
            backgroundImage: `
              linear-gradient(rgba(6,182,212,0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(6,182,212,0.1) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px',
          }}
        />
      </div>

      <div className="relative z-10 container mx-auto px-6">
        {/* Tabs with smooth transitions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="mb-20 flex items-center gap-4"
        >
          {tabs.map((tab, index) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <motion.button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as keyof typeof content)}
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
                className={`group relative rounded-lg border px-6 py-3 transition-all duration-300 ${
                  isActive
                    ? 'border-cyan-500/50 bg-cyan-500/10 text-cyan-400 shadow-lg shadow-cyan-500/20'
                    : 'border-white/10 bg-white/5 text-gray-400 hover:border-white/30 hover:bg-white/10'
                }`}
              >
                <div className="relative z-10 flex items-center gap-2">
                  <motion.div
                    animate={isActive ? { rotate: [0, 5, -5, 0] } : {}}
                    transition={{ duration: 0.5 }}
                  >
                    <Icon className="h-4 w-4" />
                  </motion.div>
                  <span className="font-mono text-xs font-semibold">{tab.label}</span>
                </div>

                {/* Animated underline */}
                {isActive && (
                  <motion.div
                    layoutId="activeTabIndicator"
                    className="absolute right-0 bottom-0 left-0 h-0.5 bg-gradient-to-r from-cyan-500 to-blue-500"
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}

                {/* Glow effect */}
                {isActive && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="absolute inset-0 -z-10 rounded-lg bg-cyan-500/5 blur-xl"
                  />
                )}
              </motion.button>
            );
          })}
        </motion.div>

        {/* Content with AnimatePresence */}
        <div className="grid items-center gap-16 lg:grid-cols-2">
          {/* Left Content */}
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: -30, filter: 'blur(10px)' }}
              animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
              exit={{ opacity: 0, x: 30, filter: 'blur(10px)' }}
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              transition={{ duration: 0.5, ease: ANIMATION_CONFIG.easing.easeOutExpo } as any}
            >
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="mb-8 flex items-center gap-4"
              >
                <motion.div
                  whileHover={{ rotate: 360, scale: 1.1 }}
                  transition={{ duration: 0.5 }}
                  className="flex h-12 w-12 items-center justify-center rounded-xl border border-white/10 bg-white/5 p-2"
                >
                  <img
                    src={content[activeTab].logo}
                    alt="Logo"
                    className="h-full w-full object-contain"
                  />
                </motion.div>
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/30"
                >
                  <span className="text-sm font-bold text-white">+</span>
                </motion.div>
                <h3 className="text-2xl font-bold text-white">{content[activeTab].title}</h3>
              </motion.div>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="mb-8 text-lg leading-relaxed text-gray-300"
              >
                {content[activeTab].description}
              </motion.p>

              <div className="space-y-4">
                {content[activeTab].features.map((feature, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + i * 0.1 }}
                    whileHover={{ x: 5, scale: 1.02 }}
                    className="flex items-center gap-3 rounded-lg p-3 text-gray-400 transition-all hover:bg-white/5"
                  >
                    <motion.span
                      animate={{ rotate: [0, 10, -10, 0] }}
                      transition={{ duration: 2, repeat: Infinity, delay: i * 0.3 }}
                      className="text-base"
                    >
                      {feature}
                    </motion.span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </AnimatePresence>

          {/* Right - Enhanced Phone Mockup */}
          <AnimatePresence mode="wait">
            <motion.div
              key={`phone-${activeTab}`}
              initial={{ opacity: 0, scale: 0.9, rotateY: -20 }}
              animate={{ opacity: 1, scale: 1, rotateY: 0 }}
              exit={{ opacity: 0, scale: 0.9, rotateY: 20 }}
              transition={{ duration: 0.5 }}
              className="relative"
              style={{ transformStyle: 'preserve-3d', perspective: '1000px' }}
            >
              {/* Glow behind phone */}
              <motion.div
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.3, 0.5, 0.3],
                }}
                transition={{ duration: 4, repeat: Infinity }}
                className="absolute inset-0 -z-10 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 blur-[60px]"
              />

              {/* Phone Frame */}
              <motion.div
                whileHover={{
                  rotateY: 10,
                  rotateX: 5,
                  scale: 1.02,
                }}
                transition={{ duration: 0.3 }}
                className="relative mx-auto max-w-[340px]"
                style={{ transformStyle: 'preserve-3d' }}
              >
                {/* Phone Bezel with gradient border */}
                <div className="relative rounded-[3rem] border-8 border-gray-950 bg-gradient-to-br from-gray-800 to-gray-900 p-3 shadow-2xl">
                  {/* Screen */}
                  <div className="relative aspect-[9/19] overflow-hidden rounded-[2.5rem] bg-black">
                    {/* Status Bar */}
                    <div className="absolute top-0 right-0 left-0 z-10 flex h-8 items-center justify-between px-8 text-xs text-white">
                      <span>9:41</span>
                      <div className="flex gap-1">
                        {[...Array(3)].map((_, i) => (
                          <motion.div
                            key={i}
                            animate={{ opacity: [0.5, 1, 0.5] }}
                            transition={{ duration: 2, repeat: Infinity, delay: i * 0.2 }}
                            className="h-3 w-4 rounded-sm border border-white/50"
                          />
                        ))}
                      </div>
                    </div>

                    {/* Animated Orb with multiple layers */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <motion.div
                        animate={{
                          scale: [1, 1.2, 1],
                          rotate: [0, 180, 360],
                        }}
                        transition={{
                          duration: 8,
                          repeat: Infinity,
                          ease: 'easeInOut',
                        }}
                        className="relative h-40 w-40"
                      >
                        {/* Outer glow */}
                        <motion.div
                          animate={{
                            scale: [1, 1.3, 1],
                            opacity: [0.3, 0.6, 0.3],
                          }}
                          transition={{
                            duration: 4,
                            repeat: Infinity,
                          }}
                          className="absolute inset-0 rounded-full bg-gradient-to-br from-cyan-500/40 to-blue-500/40 blur-2xl"
                        />

                        {/* Main orb */}
                        <motion.div
                          animate={{
                            rotate: [0, -180, -360],
                          }}
                          transition={{
                            duration: 6,
                            repeat: Infinity,
                            ease: 'linear',
                          }}
                          className="absolute inset-0 rounded-full"
                          style={{
                            background:
                              'linear-gradient(135deg, #0ea5e9 0%, #3b82f6 50%, #8b5cf6 100%)',
                            filter: 'blur(2px)',
                          }}
                        />
                      </motion.div>
                    </div>

                    {/* Text Overlay */}
                    <div className="absolute right-0 bottom-20 left-0 px-8 text-center">
                      <motion.h4
                        animate={{ opacity: [0.8, 1, 0.8] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="mb-2 text-2xl font-bold text-white"
                      >
                        Breeze
                      </motion.h4>
                      <p className="text-sm text-gray-400">Animated and earnest</p>

                      {/* Animated Dots */}
                      <div className="mt-6 flex justify-center gap-2">
                        {[...Array(9)].map((_, i) => (
                          <motion.div
                            key={i}
                            animate={{
                              scale: i === 3 ? [1, 1.3, 1] : 1,
                              opacity: i === 3 ? 1 : 0.3,
                            }}
                            transition={{
                              duration: 2,
                              repeat: Infinity,
                              delay: i * 0.1,
                            }}
                            className={`h-1.5 w-1.5 rounded-full ${
                              i === 3 ? 'bg-white' : 'bg-white/30'
                            }`}
                          />
                        ))}
                      </div>
                    </div>

                    {/* Button with hover effect */}
                    <div className="absolute right-6 bottom-6 left-6">
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="w-full rounded-full bg-white py-4 text-sm font-semibold text-black shadow-lg"
                      >
                        Start a new chat
                      </motion.button>
                    </div>
                  </div>

                  {/* Notch */}
                  <div className="absolute top-3 left-1/2 z-20 h-7 w-32 -translate-x-1/2 rounded-b-3xl bg-black" />
                </div>
              </motion.div>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
}
