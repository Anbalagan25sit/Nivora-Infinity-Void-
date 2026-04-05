'use client';

import { motion } from 'motion/react';
import { Check, X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

const features = [
  'Voice interaction',
  'Offline / local mode',
  'Workflow automation (n8n)',
  'Browser control',
  'Persistent memory',
  'Open source',
  'Plugin ecosystem',
  'Screen understanding',
  'Multi-LLM support',
  'Free to use',
];

const competitors = [
  {
    name: 'Nivora',
    highlight: true,
    values: [true, true, true, true, true, true, true, true, true, true],
  },
  {
    name: 'Claude Cowork',
    highlight: false,
    values: [false, false, false, true, false, false, false, false, false, false],
  },
  {
    name: 'Comet Agent',
    highlight: false,
    values: [true, false, false, false, false, false, false, false, false, false],
  },
];

function ComparisonRow({ feature, values, index }: { feature: string; values: boolean[]; index: number }) {
  const [isVisible, setIsVisible] = useState(false);
  const rowRef = useRef<HTMLTableRowElement>(null);

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

    if (rowRef.current) {
      observer.observe(rowRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <motion.tr
      ref={rowRef}
      initial={{ opacity: 0, x: -20 }}
      animate={isVisible ? { opacity: 1, x: 0 } : {}}
      transition={{ duration: 0.5, delay: index * 0.05 }}
      className="border-b border-white/5"
    >
      <td className="py-5 px-6 text-gray-300 font-medium">{feature}</td>
      {values.map((value, i) => (
        <td key={i} className="py-5 px-6 text-center">
          {value ? (
            <Check className="w-5 h-5 text-green-500 mx-auto" />
          ) : (
            <X className="w-5 h-5 text-gray-600 mx-auto" />
          )}
        </td>
      ))}
    </motion.tr>
  );
}

export function ComparisonSection() {
  return (
    <section id="comparison" className="relative py-32 bg-black">
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
              Why Nivora beats the rest
            </span>
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            The most complete AI agent platform, bar none.
          </p>
        </motion.div>

        {/* Comparison Table */}
        <div className="max-w-5xl mx-auto overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="py-6 px-6 text-left text-gray-400 font-semibold text-sm uppercase tracking-wider">
                  Feature
                </th>
                {competitors.map((competitor) => (
                  <th key={competitor.name} className="py-6 px-6 text-center relative">
                    {competitor.highlight && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.3 }}
                        className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-gradient-to-r from-purple-600 to-purple-500 text-white text-xs font-bold whitespace-nowrap"
                      >
                        Most Powerful
                      </motion.div>
                    )}
                    <div
                      className={`text-lg font-bold ${
                        competitor.highlight
                          ? 'text-transparent bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text'
                          : 'text-gray-500'
                      }`}
                    >
                      {competitor.name}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {features.map((feature, index) => (
                <ComparisonRow
                  key={feature}
                  feature={feature}
                  values={competitors.map((c) => c.values[index])}
                  index={index}
                />
              ))}
            </tbody>
          </table>
        </div>

        {/* Highlighted Column Border */}
        <div className="max-w-5xl mx-auto mt-8">
          <div className="grid grid-cols-4 gap-0">
            <div />
            <div className="border-2 border-purple-500/30 rounded-xl h-4 relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-cyan-500/10 blur-xl" />
            </div>
            <div />
            <div />
          </div>
        </div>
      </div>
    </section>
  );
}
