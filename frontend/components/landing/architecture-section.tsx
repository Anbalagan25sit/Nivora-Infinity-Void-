'use client';

import { Brain, Mic, Workflow, Zap } from 'lucide-react';
import { motion } from 'motion/react';

export function ArchitectureSection() {
  return (
    <section
      id="how-it-works"
      className="relative overflow-hidden bg-gradient-to-b from-[#0a0a0a] to-black py-32"
    >
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 h-[800px] w-[800px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-gradient-to-r from-purple-600/10 to-blue-600/10 blur-[150px]" />

      <div className="relative z-10 container mx-auto px-6">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mb-24 text-center"
        >
          <h2 className="mb-6 text-5xl font-bold md:text-6xl">
            <span className="bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              How Nivora works
            </span>
          </h2>
          <p className="mx-auto max-w-2xl text-xl text-gray-400">
            Real-time voice → AI intelligence → Automated actions
          </p>
        </motion.div>

        {/* Architecture Diagram */}
        <div className="mx-auto mb-24 max-w-6xl">
          <svg viewBox="0 0 1200 400" className="h-auto w-full">
            {/* Animated Connection Lines */}
            <motion.path
              d="M 150 200 L 300 200"
              stroke="url(#blueGradient)"
              strokeWidth="3"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1, repeat: Infinity, repeatDelay: 3, ease: 'easeInOut' }}
            />
            <motion.path
              d="M 450 200 L 600 120"
              stroke="url(#purpleGradient)"
              strokeWidth="3"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{
                duration: 1,
                delay: 1,
                repeat: Infinity,
                repeatDelay: 3,
                ease: 'easeInOut',
              }}
            />
            <motion.path
              d="M 450 200 L 600 200"
              stroke="url(#greenGradient)"
              strokeWidth="3"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{
                duration: 1,
                delay: 1,
                repeat: Infinity,
                repeatDelay: 3,
                ease: 'easeInOut',
              }}
            />
            <motion.path
              d="M 450 200 L 600 280"
              stroke="url(#purpleGradient)"
              strokeWidth="3"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{
                duration: 1,
                delay: 1,
                repeat: Infinity,
                repeatDelay: 3,
                ease: 'easeInOut',
              }}
            />
            <motion.path
              d="M 800 120 L 950 200"
              stroke="url(#orangeGradient)"
              strokeWidth="3"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{
                duration: 1,
                delay: 2,
                repeat: Infinity,
                repeatDelay: 3,
                ease: 'easeInOut',
              }}
            />
            <motion.path
              d="M 800 200 L 950 200"
              stroke="url(#orangeGradient)"
              strokeWidth="3"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{
                duration: 1,
                delay: 2,
                repeat: Infinity,
                repeatDelay: 3,
                ease: 'easeInOut',
              }}
            />
            <motion.path
              d="M 800 280 L 950 200"
              stroke="url(#orangeGradient)"
              strokeWidth="3"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{
                duration: 1,
                delay: 2,
                repeat: Infinity,
                repeatDelay: 3,
                ease: 'easeInOut',
              }}
            />

            {/* Gradient Definitions */}
            <defs>
              <linearGradient id="blueGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity="1" />
              </linearGradient>
              <linearGradient id="purpleGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#a855f7" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#a855f7" stopOpacity="1" />
              </linearGradient>
              <linearGradient id="greenGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#10b981" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#10b981" stopOpacity="1" />
              </linearGradient>
              <linearGradient id="orangeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#f97316" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#f97316" stopOpacity="1" />
              </linearGradient>
            </defs>

            {/* Nodes */}
            <g>
              {/* User Voice */}
              <rect x="50" y="180" width="150" height="40" rx="20" fill="#1e40af" />
              <text x="125" y="205" textAnchor="middle" fill="white" fontSize="14" fontWeight="600">
                🎤 User Voice
              </text>

              {/* LiveKit */}
              <rect x="250" y="180" width="200" height="40" rx="20" fill="#3b82f6" />
              <text x="350" y="205" textAnchor="middle" fill="white" fontSize="14" fontWeight="600">
                ⚡ LiveKit (Real-time)
              </text>

              {/* Agent Core */}
              <rect x="500" y="180" width="200" height="40" rx="20" fill="#6366f1" />
              <text x="600" y="205" textAnchor="middle" fill="white" fontSize="14" fontWeight="600">
                🧠 Agent Core (Python)
              </text>

              {/* AWS Nova Pro */}
              <rect x="750" y="100" width="180" height="40" rx="20" fill="#a855f7" />
              <text x="840" y="125" textAnchor="middle" fill="white" fontSize="14" fontWeight="600">
                🤖 AWS Nova Pro
              </text>

              {/* n8n Workflows */}
              <rect x="750" y="180" width="180" height="40" rx="20" fill="#10b981" />
              <text x="840" y="205" textAnchor="middle" fill="white" fontSize="14" fontWeight="600">
                🔄 n8n Workflows
              </text>

              {/* Ollama */}
              <rect x="750" y="260" width="180" height="40" rx="20" fill="#a855f7" />
              <text x="840" y="285" textAnchor="middle" fill="white" fontSize="14" fontWeight="600">
                💻 Ollama (Local)
              </text>

              {/* Actions */}
              <rect x="1000" y="180" width="150" height="40" rx="20" fill="#f97316" />
              <text
                x="1075"
                y="205"
                textAnchor="middle"
                fill="white"
                fontSize="14"
                fontWeight="600"
              >
                ⚡ Actions
              </text>
            </g>
          </svg>
        </div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mx-auto grid max-w-4xl grid-cols-1 gap-8 md:grid-cols-3"
        >
          <div className="rounded-2xl border border-white/10 bg-white/5 p-8 text-center backdrop-blur-sm">
            <div className="mb-2 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-5xl font-bold text-transparent">
              &lt;200ms
            </div>
            <div className="text-sm tracking-wider text-gray-400 uppercase">Voice latency</div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/5 p-8 text-center backdrop-blur-sm">
            <div className="mb-2 bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-5xl font-bold text-transparent">
              400+
            </div>
            <div className="text-sm tracking-wider text-gray-400 uppercase">n8n integrations</div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/5 p-8 text-center backdrop-blur-sm">
            <div className="mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-5xl font-bold text-transparent">
              100%
            </div>
            <div className="text-sm tracking-wider text-gray-400 uppercase">Local by default</div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
