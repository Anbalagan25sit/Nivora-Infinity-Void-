'use client';

import { motion } from 'motion/react';

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

export function CompanyLogosSection() {
  return (
    <section className="relative py-12 bg-black border-y border-white/5 overflow-hidden">
      <div className="container mx-auto px-6">
        <h3 className="text-gray-500 text-sm font-medium mb-8">
          Powering billions of calls in production for:
        </h3>

        {/* Infinite Scroll Marquee */}
        <div className="relative">
          <div className="marquee-wrapper">
            <div className="flex gap-16 marquee-track">
              {/* First set */}
              {companyLogos.map((logo, i) => (
                <div
                  key={`${logo.name}-1-${i}`}
                  className="flex items-center justify-center min-w-[140px] h-16 brightness-0 invert opacity-40 hover:brightness-100 hover:invert-0 hover:opacity-100 transition-all duration-300"
                >
                  <img src={logo.src} alt={logo.name} className="max-h-10 max-w-[120px] object-contain" />
                </div>
              ))}
              {/* Duplicate for seamless loop */}
              {companyLogos.map((logo, i) => (
                <div
                  key={`${logo.name}-2-${i}`}
                  className="flex items-center justify-center min-w-[140px] h-16 brightness-0 invert opacity-40 hover:brightness-100 hover:invert-0 hover:opacity-100 transition-all duration-300"
                >
                  <img src={logo.src} alt={logo.name} className="max-h-10 max-w-[120px] object-contain" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
