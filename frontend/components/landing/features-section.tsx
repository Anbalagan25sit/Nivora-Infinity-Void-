'use client';

import { useEffect, useRef, useState } from 'react';
import { Brain, Eye, Mic, Plug, WifiOff, Workflow } from 'lucide-react';
import { motion } from 'motion/react';

const features = [
  {
    icon: Mic,
    title: 'Voice First',
    description:
      'Talk to your computer naturally. Sub-200ms latency powered by LiveKit real-time infrastructure.',
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
    description:
      'AWS Nova Pro vision understands your screen in real time. Fill forms, read content, navigate apps.',
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
    description:
      'Nivora remembers your projects, preferences, and past conversations across sessions.',
    color: 'from-pink-500 to-pink-600',
  },
  {
    icon: Plug,
    title: 'Plugin Ecosystem',
    description: 'Community-built tools via n8n MCP. Extend Nivora for any workflow imaginable.',
    color: 'from-orange-500 to-orange-600',
  },
];

function FeatureCard({ feature, index }: { feature: (typeof features)[0]; index: number }) {
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
      className="group relative rounded-2xl border border-[#222222] bg-[#111111] p-8 transition-all duration-300 hover:border-purple-500/50"
    >
      {/* Glow Effect on Hover */}
      <div className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br from-purple-500/10 via-transparent to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />

      {/* Icon */}
      <div
        className={`relative mb-6 h-14 w-14 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center`}
      >
        <Icon className="h-7 w-7 text-white" />
      </div>

      {/* Content */}
      <h3 className="relative mb-3 text-2xl font-bold text-white">{feature.title}</h3>
      <p className="relative leading-relaxed text-gray-400">{feature.description}</p>

      {/* Hover Border Glow */}
      <div className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100">
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-purple-500/20 to-cyan-500/20 blur-xl" />
      </div>
    </motion.div>
  );
}

export function FeaturesSection() {
  return (
    <section id="features" className="relative bg-[#0a0a0a] py-32">
      <div className="container mx-auto px-6">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mb-20 text-center"
        >
          <h2 className="mb-6 text-5xl font-bold md:text-6xl">
            <span className="bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              Built for power users
            </span>
          </h2>
          <p className="mx-auto max-w-2xl text-xl text-gray-400">
            Every feature designed to make AI agents fast, private, and infinitely extensible.
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <FeatureCard key={feature.title} feature={feature} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
}
