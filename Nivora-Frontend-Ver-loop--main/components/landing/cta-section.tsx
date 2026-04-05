'use client';

import { motion } from 'motion/react';
import { Github, Twitter, MessageCircle, ArrowRight } from 'lucide-react';

export function CTASection() {
  return (
    <section className="relative py-32 bg-gradient-to-b from-black to-[#0a0a0a] overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[600px] rounded-full bg-gradient-to-r from-purple-600/20 to-cyan-600/20 blur-[150px]" />

      <div className="container mx-auto px-6 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto text-center"
        >
          <h2 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="bg-gradient-to-r from-white via-purple-200 to-cyan-200 bg-clip-text text-transparent">
              Ready to take control?
            </span>
          </h2>
          <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto">
            Join thousands of developers building the future of AI agents. Open source, privacy-first, infinitely extensible.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <button className="group relative px-10 py-5 rounded-full bg-gradient-to-r from-purple-600 to-purple-500 text-white font-bold text-lg overflow-hidden transition-all hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/50">
              <span className="relative z-10 flex items-center gap-2">
                Download Nivora
                <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-purple-600 opacity-0 group-hover:opacity-100 transition-opacity" />
            </button>

            <button className="group px-10 py-5 rounded-full border-2 border-white/20 text-white font-bold text-lg transition-all hover:border-white/40 hover:bg-white/5 flex items-center gap-2">
              <Github className="w-5 h-5" />
              View Source Code
            </button>
          </div>

          {/* Social Links */}
          <div className="flex items-center justify-center gap-6">
            <a
              href="https://github.com/nivora"
              target="_blank"
              rel="noopener noreferrer"
              className="w-12 h-12 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:border-white/30 transition-all"
            >
              <Github className="w-5 h-5" />
            </a>
            <a
              href="https://twitter.com/nivora"
              target="_blank"
              rel="noopener noreferrer"
              className="w-12 h-12 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:border-white/30 transition-all"
            >
              <Twitter className="w-5 h-5" />
            </a>
            <a
              href="https://discord.gg/nivora"
              target="_blank"
              rel="noopener noreferrer"
              className="w-12 h-12 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:border-white/30 transition-all"
            >
              <MessageCircle className="w-5 h-5" />
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

export function Footer() {
  return (
    <footer className="relative py-12 bg-black border-t border-white/5">
      <div className="container mx-auto px-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Logo & Copyright */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-600 to-cyan-600 flex items-center justify-center font-bold text-white text-sm">
              N
            </div>
            <div>
              <div className="text-white font-semibold">Nivora</div>
              <div className="text-gray-500 text-xs">© 2024 Open Source</div>
            </div>
          </div>

          {/* Links */}
          <div className="flex items-center gap-8">
            <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">
              Documentation
            </a>
            <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">
              Community
            </a>
            <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">
              Contributing
            </a>
            <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">
              License
            </a>
          </div>

          {/* Badge */}
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10">
            <span className="text-xs text-gray-400">Powered by</span>
            <span className="text-xs font-semibold text-purple-400">LiveKit</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
