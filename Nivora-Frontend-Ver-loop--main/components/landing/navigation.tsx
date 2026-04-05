'use client';

import { motion } from 'motion/react';
import { Github, Star } from 'lucide-react';

export function Navigation() {
  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className="fixed top-0 left-0 right-0 z-50 px-6 py-6"
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-600 to-cyan-600 flex items-center justify-center font-bold text-white">
            N
          </div>
          <span className="text-xl font-bold text-white">Nivora</span>
        </div>

        {/* Nav Links */}
        <div className="hidden md:flex items-center gap-8">
          <a href="#features" className="text-gray-300 hover:text-white transition-colors">
            Features
          </a>
          <a href="#how-it-works" className="text-gray-300 hover:text-white transition-colors">
            How it works
          </a>
          <a href="#comparison" className="text-gray-300 hover:text-white transition-colors">
            Comparison
          </a>
          <a href="https://docs.nivora.ai" className="text-gray-300 hover:text-white transition-colors">
            Docs
          </a>
        </div>

        {/* CTA */}
        <div className="flex items-center gap-4">
          <a
            href="https://github.com/nivora/nivora"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden md:flex items-center gap-2 px-4 py-2 rounded-lg border border-white/20 text-white hover:border-white/40 hover:bg-white/5 transition-all"
          >
            <Star className="w-4 h-4" />
            <span className="text-sm font-medium">Star on GitHub</span>
          </a>
          <a
            href="#download"
            className="px-5 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-purple-500 text-white font-semibold text-sm hover:scale-105 transition-transform"
          >
            Download
          </a>
        </div>
      </div>
    </motion.nav>
  );
}
