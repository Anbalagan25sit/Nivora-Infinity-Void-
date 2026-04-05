'use client';

import { motion } from 'motion/react';
import { useEffect, useState } from 'react';

const companyLogos = [
  { name: 'AWS', src: '/aws-2.svg' },
  { name: 'ChatGPT', src: '/chatgpt-3.svg' },
  { name: 'Claude', src: '/claude-3.svg' },
  { name: 'Gemini', src: '/gemini-ai.svg' },
  { name: 'Google Sheets', src: '/google-sheets-full-logo-1.svg' },
  { name: 'Microsoft Azure', src: '/microsoft-azure-2.svg' },
  { name: 'Gmail', src: '/official-gmail-icon-2020-.svg' },
  { name: 'Spotify', src: '/spotify-logo.svg' },
  { name: 'YouTube', src: '/youtube-6.svg' },
];

export function EnhancedCompanyLogosSection() {
  const [isPaused, setIsPaused] = useState(false);

  return (
    <section className="relative py-16 bg-black border-y border-white/5 overflow-hidden">
      {/* Gradient fade edges */}
      <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-black to-transparent z-10 pointer-events-none" />
      <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-black to-transparent z-10 pointer-events-none" />

      <div className="container mx-auto px-6">
        {/* Title with fade in */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="flex items-center gap-8 mb-8"
        >
          <h3 className="text-gray-500 text-sm font-medium whitespace-nowrap">
            Powering billions of calls in production for:
          </h3>
          <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
        </motion.div>

        {/* Infinite Scroll Marquee with pause on hover */}
        <div
          className="relative"
          onMouseEnter={() => setIsPaused(true)}
          onMouseLeave={() => setIsPaused(false)}
        >
          <div className="flex overflow-hidden">
            <motion.div
              animate={{
                x: isPaused ? 0 : [0, -1800],
              }}
              transition={{
                x: {
                  duration: 30,
                  repeat: Infinity,
                  ease: 'linear',
                },
              }}
              className="flex gap-16 shrink-0"
            >
              {/* First set */}
              {companyLogos.map((logo, i) => (
                <motion.div
                  key={`${logo.name}-1-${i}`}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  whileHover={{
                    scale: 1.1,
                    filter: 'brightness(0) invert(1)',
                  }}
                  className="flex items-center justify-center min-w-[140px] h-16 brightness-0 invert opacity-40 transition-all duration-300 cursor-pointer"
                >
                  <img
                    src={logo.src}
                    alt={logo.name}
                    className="max-h-10 max-w-[120px] object-contain"
                    loading="lazy"
                  />
                </motion.div>
              ))}

              {/* Duplicate for seamless loop */}
              {companyLogos.map((logo, i) => (
                <motion.div
                  key={`${logo.name}-2-${i}`}
                  whileHover={{
                    scale: 1.1,
                    filter: 'brightness(0) invert(1)',
                  }}
                  className="flex items-center justify-center min-w-[140px] h-16 brightness-0 invert opacity-40 transition-all duration-300 cursor-pointer"
                >
                  <img
                    src={logo.src}
                    alt={logo.name}
                    className="max-h-10 max-w-[120px] object-contain"
                    loading="lazy"
                  />
                </motion.div>
              ))}

              {/* Third set for extra smooth loop */}
              {companyLogos.map((logo, i) => (
                <motion.div
                  key={`${logo.name}-3-${i}`}
                  whileHover={{
                    scale: 1.1,
                    filter: 'brightness(0) invert(1)',
                  }}
                  className="flex items-center justify-center min-w-[140px] h-16 brightness-0 invert opacity-40 transition-all duration-300 cursor-pointer"
                >
                  <img
                    src={logo.src}
                    alt={logo.name}
                    className="max-h-10 max-w-[120px] object-contain"
                    loading="lazy"
                  />
                </motion.div>
              ))}
            </motion.div>
          </div>
        </div>
      </div>

      {/* Bottom glow effect */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-px bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent" />
    </section>
  );
}
