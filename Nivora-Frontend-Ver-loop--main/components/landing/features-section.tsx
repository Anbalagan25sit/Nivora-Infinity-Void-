'use client';

import { motion } from 'motion/react';
import { useEffect, useRef, useState } from 'react';
import { Mic, Workflow, Eye, WifiOff, Brain, Plug } from 'lucide-react';

const features = [
  {
    icon: Mic,
    title: 'Voice First',
    description: 'Talk to your computer naturally. Sub-200ms latency powered by LiveKit real-time infrastructure.',
    color: 'from-purple-500 to-purple-600',
  },
  {
    icon: Workflow,
    title: 'n8n Workflows',
    description: '400+ integrations. Email, Calendar, Spotify, Notion — all triggered by voice.',
    color: 'from-blue-500 to-blue-600',
  },
  {
    icon: Eye,
    title: 'Screen Intelligence',
    description: 'AWS Nova Pro vision understands your screen in real time. Fill forms, read content, navigate apps.',
    color: 'from-cyan-500 to-cyan-600',
  },
  {
    icon: WifiOff,
    title: 'Works Offline',
    description: 'Local LLMs via Ollama. Your data never leaves your machine unless you choose.',
    color: 'from-green-500 to-green-600',
  },
  {
    icon: Brain,
    title: 'Persistent Memory',
    description: 'Nivora remembers your projects, preferences, and past conversations across sessions.',
    color: 'from-pink-500 to-pink-600',
  },
  {
    icon: Plug,
    title: 'Plugin Ecosystem',
    description: 'Community-built tools via n8n MCP. Extend Nivora for any workflow imaginable.',
    color: 'from-orange-500 to-orange-600',
  },
];

function FeatureCard({ feature, index }: { feature: typeof features[0]; index: number }) {
  const [isVisible, setIsVisible] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (cardRef.current) {
      observer.observe(cardRef.current);
    }

    return () => observer.disconnect();
  }, []);

  const Icon = feature.icon;

  return (
    <motion.div
      ref={cardRef}
      initial={{ opacity: 0, y: 30 }}
      animate={isVisible ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, delay: index * 0.1 }}
      className="group relative p-8 rounded-2xl bg-[#111111] border border-[#222222] hover:border-purple-500/50 transition-all duration-300"
    >
      {/* Glow Effect on Hover */}
      <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-br from-purple-500/10 via-transparent to-transparent pointer-events-none" />

      {/* Icon */}
      <div className={`relative mb-6 w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center`}>
        <Icon className="w-7 h-7 text-white" />
      </div>

      {/* Content */}
      <h3 className="relative text-2xl font-bold text-white mb-3">
        {feature.title}
      </h3>
      <p className="relative text-gray-400 leading-relaxed">
        {feature.description}
      </p>

      {/* Hover Border Glow */}
      <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-purple-500/20 to-cyan-500/20 blur-xl" />
      </div>
    </motion.div>
  );
}

export function FeaturesSection() {
  return (
    <section id="features" className="relative py-32 bg-[#0a0a0a]">
      <div className="container mx-auto px-6">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-20"
        >
          <h2 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              Built for power users
            </span>
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Every feature designed to make AI agents fast, private, and infinitely extensible.
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
          {features.map((feature, index) => (
            <FeatureCard key={feature.title} feature={feature} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
}
