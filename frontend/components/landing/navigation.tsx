'use client';

import { Github, Star } from 'lucide-react';
import { motion } from 'motion/react';

export function Navigation() {
  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className="fixed top-0 right-0 left-0 z-50 px-6 py-6"
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-purple-600 to-cyan-600 font-bold text-white">
            N
          </div>
          <span className="text-xl font-bold text-white">Nivora</span>
        </div>

        {/* Nav Links */}
        <div className="hidden items-center gap-8 md:flex">
          <a href="#features" className="text-gray-300 transition-colors hover:text-white">
            Features
          </a>
          <a href="#how-it-works" className="text-gray-300 transition-colors hover:text-white">
            How it works
          </a>
          <a href="#comparison" className="text-gray-300 transition-colors hover:text-white">
            Comparison
          </a>
          <a
            href="https://docs.nivora.ai"
            className="text-gray-300 transition-colors hover:text-white"
          >
            Docs
          </a>
        </div>

        {/* CTA */}
        <div className="flex items-center gap-4">
          <a
            href="https://github.com/nivora/nivora"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden items-center gap-2 rounded-lg border border-white/20 px-4 py-2 text-white transition-all hover:border-white/40 hover:bg-white/5 md:flex"
          >
            <Star className="h-4 w-4" />
            <span className="text-sm font-medium">Star on GitHub</span>
          </a>
          <a
            href="#download"
            className="rounded-lg bg-gradient-to-r from-purple-600 to-purple-500 px-5 py-2 text-sm font-semibold text-white transition-transform hover:scale-105"
          >
            Download
          </a>
        </div>
      </div>
    </motion.nav>
  );
}
