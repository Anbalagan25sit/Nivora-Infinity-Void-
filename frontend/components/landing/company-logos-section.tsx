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
    <section className="relative overflow-hidden border-y border-white/5 bg-black py-12">
      <div className="container mx-auto px-6">
        <h3 className="mb-8 text-sm font-medium text-gray-500">
          Powering billions of calls in production for:
        </h3>

        {/* Infinite Scroll Marquee */}
        <div className="relative">
          <div className="marquee-wrapper">
            <div className="marquee-track flex gap-16">
              {/* First set */}
              {companyLogos.map((logo, i) => (
                <div
                  key={`${logo.name}-1-${i}`}
                  className="flex h-16 min-w-[140px] items-center justify-center opacity-40 brightness-0 invert transition-all duration-300 hover:opacity-100 hover:brightness-100 hover:invert-0"
                >
                  <img
                    src={logo.src}
                    alt={logo.name}
                    className="max-h-10 max-w-[120px] object-contain"
                  />
                </div>
              ))}
              {/* Duplicate for seamless loop */}
              {companyLogos.map((logo, i) => (
                <div
                  key={`${logo.name}-2-${i}`}
                  className="flex h-16 min-w-[140px] items-center justify-center opacity-40 brightness-0 invert transition-all duration-300 hover:opacity-100 hover:brightness-100 hover:invert-0"
                >
                  <img
                    src={logo.src}
                    alt={logo.name}
                    className="max-h-10 max-w-[120px] object-contain"
                  />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
