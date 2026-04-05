'use client';

import { motion, AnimatePresence, useInView } from 'motion/react';
import { useState, useRef } from 'react';
import { Mic2, Video, Bot } from 'lucide-react';
import { ANIMATION_CONFIG, fadeInUp, fadeInLeft } from '@/lib/animations';

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
  const [activeTab, setActiveTab] = useState('voice');
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.3 });

  return (
    <section ref={ref} className="relative py-32 bg-black overflow-hidden">
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

      <div className="container mx-auto px-6 relative z-10">
        {/* Tabs with smooth transitions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="flex items-center gap-4 mb-20"
        >
          {tabs.map((tab, index) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <motion.button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
                className={`group relative px-6 py-3 rounded-lg border transition-all duration-300 ${
                  isActive
                    ? 'bg-cyan-500/10 border-cyan-500/50 text-cyan-400 shadow-lg shadow-cyan-500/20'
                    : 'bg-white/5 border-white/10 text-gray-400 hover:border-white/30 hover:bg-white/10'
                }`}
              >
                <div className="flex items-center gap-2 relative z-10">
                  <motion.div
                    animate={isActive ? { rotate: [0, 5, -5, 0] } : {}}
                    transition={{ duration: 0.5 }}
                  >
                    <Icon className="w-4 h-4" />
                  </motion.div>
                  <span className="text-xs font-mono font-semibold">{tab.label}</span>
                </div>

                {/* Animated underline */}
                {isActive && (
                  <motion.div
                    layoutId="activeTabIndicator"
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-500 to-blue-500"
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}

                {/* Glow effect */}
                {isActive && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="absolute inset-0 bg-cyan-500/5 rounded-lg blur-xl -z-10"
                  />
                )}
              </motion.button>
            );
          })}
        </motion.div>

        {/* Content with AnimatePresence */}
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left Content */}
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: -30, filter: 'blur(10px)' }}
              animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
              exit={{ opacity: 0, x: 30, filter: 'blur(10px)' }}
              transition={{ duration: 0.5, ease: ANIMATION_CONFIG.easing.easeOutExpo }}
            >
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="flex items-center gap-4 mb-8"
              >
                <motion.div
                  whileHover={{ rotate: 360, scale: 1.1 }}
                  transition={{ duration: 0.5 }}
                  className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center p-2"
                >
                  <img src={content[activeTab].logo} alt="Logo" className="w-full h-full object-contain" />
                </motion.div>
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30"
                >
                  <span className="text-white text-sm font-bold">+</span>
                </motion.div>
                <h3 className="text-2xl font-bold text-white">{content[activeTab].title}</h3>
              </motion.div>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-lg text-gray-300 mb-8 leading-relaxed"
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
                    className="flex items-center gap-3 text-gray-400 p-3 rounded-lg hover:bg-white/5 transition-all"
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
                className="absolute inset-0 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 blur-[60px] -z-10"
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
                <div className="relative rounded-[3rem] bg-gradient-to-br from-gray-800 to-gray-900 p-3 shadow-2xl border-8 border-gray-950">
                  {/* Screen */}
                  <div className="relative rounded-[2.5rem] bg-black overflow-hidden aspect-[9/19]">
                    {/* Status Bar */}
                    <div className="absolute top-0 left-0 right-0 h-8 flex items-center justify-between px-8 text-white text-xs z-10">
                      <span>9:41</span>
                      <div className="flex gap-1">
                        {[...Array(3)].map((_, i) => (
                          <motion.div
                            key={i}
                            animate={{ opacity: [0.5, 1, 0.5] }}
                            transition={{ duration: 2, repeat: Infinity, delay: i * 0.2 }}
                            className="w-4 h-3 border border-white/50 rounded-sm"
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
                        className="relative w-40 h-40"
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
                            background: 'linear-gradient(135deg, #0ea5e9 0%, #3b82f6 50%, #8b5cf6 100%)',
                            filter: 'blur(2px)',
                          }}
                        />
                      </motion.div>
                    </div>

                    {/* Text Overlay */}
                    <div className="absolute bottom-20 left-0 right-0 text-center px-8">
                      <motion.h4
                        animate={{ opacity: [0.8, 1, 0.8] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="text-white text-2xl font-bold mb-2"
                      >
                        Breeze
                      </motion.h4>
                      <p className="text-gray-400 text-sm">Animated and earnest</p>

                      {/* Animated Dots */}
                      <div className="flex justify-center gap-2 mt-6">
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
                            className={`w-1.5 h-1.5 rounded-full ${
                              i === 3 ? 'bg-white' : 'bg-white/30'
                            }`}
                          />
                        ))}
                      </div>
                    </div>

                    {/* Button with hover effect */}
                    <div className="absolute bottom-6 left-6 right-6">
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="w-full py-4 rounded-full bg-white text-black font-semibold text-sm shadow-lg"
                      >
                        Start a new chat
                      </motion.button>
                    </div>
                  </div>

                  {/* Notch */}
                  <div className="absolute top-3 left-1/2 -translate-x-1/2 w-32 h-7 bg-black rounded-b-3xl z-20" />
                </div>
              </motion.div>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
}
