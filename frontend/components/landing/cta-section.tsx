'use client';

import { ArrowRight, Github, MessageCircle, Twitter } from 'lucide-react';
import { motion } from 'motion/react';

export function CTASection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-black to-[#0a0a0a] py-32">
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 h-[600px] w-[1000px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-gradient-to-r from-purple-600/20 to-cyan-600/20 blur-[150px]" />

      <div className="relative z-10 container mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mx-auto max-w-4xl text-center"
        >
          <h2 className="mb-6 text-5xl font-bold md:text-6xl">
            <span className="bg-gradient-to-r from-white via-purple-200 to-cyan-200 bg-clip-text text-transparent">
              Ready to take control?
            </span>
          </h2>
          <p className="mx-auto mb-12 max-w-2xl text-xl text-gray-400">
            Join thousands of developers building the future of AI agents. Open source,
            privacy-first, infinitely extensible.
          </p>

          <div className="mb-16 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <button className="group relative overflow-hidden rounded-full bg-gradient-to-r from-purple-600 to-purple-500 px-10 py-5 text-lg font-bold text-white transition-all hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/50">
              <span className="relative z-10 flex items-center gap-2">
                Download Nivora
                <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-purple-600 opacity-0 transition-opacity group-hover:opacity-100" />
            </button>

            <button className="group flex items-center gap-2 rounded-full border-2 border-white/20 px-10 py-5 text-lg font-bold text-white transition-all hover:border-white/40 hover:bg-white/5">
              <Github className="h-5 w-5" />
              View Source Code
            </button>
          </div>

          {/* Social Links */}
          <div className="flex items-center justify-center gap-6">
            <a
              href="https://github.com/nivora"
              target="_blank"
              rel="noopener noreferrer"
              className="flex h-12 w-12 items-center justify-center rounded-full border border-white/10 bg-white/5 text-gray-400 transition-all hover:border-white/30 hover:text-white"
            >
              <Github className="h-5 w-5" />
            </a>
            <a
              href="https://twitter.com/nivora"
              target="_blank"
              rel="noopener noreferrer"
              className="flex h-12 w-12 items-center justify-center rounded-full border border-white/10 bg-white/5 text-gray-400 transition-all hover:border-white/30 hover:text-white"
            >
              <Twitter className="h-5 w-5" />
            </a>
            <a
              href="https://discord.gg/nivora"
              target="_blank"
              rel="noopener noreferrer"
              className="flex h-12 w-12 items-center justify-center rounded-full border border-white/10 bg-white/5 text-gray-400 transition-all hover:border-white/30 hover:text-white"
            >
              <MessageCircle className="h-5 w-5" />
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

export function Footer() {
  return (
    <footer className="relative border-t border-white/5 bg-black py-12">
      <div className="container mx-auto px-6">
        <div className="flex flex-col items-center justify-between gap-6 md:flex-row">
          {/* Logo & Copyright */}
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-purple-600 to-cyan-600 text-sm font-bold text-white">
              N
            </div>
            <div>
              <div className="font-semibold text-white">Nivora</div>
              <div className="text-xs text-gray-500">© 2024 Open Source</div>
            </div>
          </div>

          {/* Links */}
          <div className="flex items-center gap-8">
            <a href="#" className="text-sm text-gray-400 transition-colors hover:text-white">
              Documentation
            </a>
            <a href="#" className="text-sm text-gray-400 transition-colors hover:text-white">
              Community
            </a>
            <a href="#" className="text-sm text-gray-400 transition-colors hover:text-white">
              Contributing
            </a>
            <a href="#" className="text-sm text-gray-400 transition-colors hover:text-white">
              License
            </a>
          </div>

          {/* Badge */}
          <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2">
            <span className="text-xs text-gray-400">Powered by</span>
            <span className="text-xs font-semibold text-purple-400">LiveKit</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
