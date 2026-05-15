'use client';

import React, { useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { useSessionContext, useSessionMessages } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { AgentControlBar } from '@/components/agents-ui/agent-control-bar';
import { AudioVisualizer } from '@/components/app/audio-visualizer';
import { ChatTranscript } from '@/components/app/chat-transcript';
import { VoidBackground } from '@/components/app/void-background';
import { cn } from '@/lib/shadcn/utils';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const BOTTOM_VIEW_MOTION_PROPS: any = {
  variants: {
    visible: { opacity: 1, translateY: '0%' },
    hidden: { opacity: 0, translateY: '100%' },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: { duration: 0.3, delay: 0.5, ease: 'easeOut' },
};

interface SessionViewProps {
  appConfig: AppConfig;
  onDisconnect: () => void;
}

export function SessionView({ appConfig, onDisconnect }: SessionViewProps) {
  const { session } = useSessionContext();
  const [isChatOpen, setIsChatOpen] = useState(false);
  const messages = useSessionMessages();

  // If there's an agent in the room
  const hasAgent = true; // For now assuming we always have an agent connecting

  return (
    <div className="relative flex h-screen w-full flex-col items-center justify-center overflow-hidden font-sans text-white">
      <VoidBackground />

      {/* Header section */}
      <div className="absolute top-10 z-10 flex w-full flex-col items-center justify-center space-y-2">
        <h1 className="bg-gradient-to-r from-blue-100 to-blue-300 bg-clip-text text-4xl font-light tracking-wide text-transparent opacity-90 md:text-5xl">
          {appConfig.pageTitle || 'Voice Playground'}
        </h1>
        <p className="text-sm tracking-widest uppercase opacity-50 md:text-base">
          {appConfig.pageDescription || 'YOUR AI COMPANION AWAITS'}
        </p>
      </div>

      {/* Main Orb / Visualizer */}
      <div className="relative z-10 flex w-full flex-1 flex-col items-center justify-center">
        <div className="group relative cursor-pointer">
          <AudioVisualizer
            appConfig={{
              ...appConfig,
              audioVisualizerType: 'aura',
              audioVisualizerColor: '#1FD5F9',
            }}
            isChatOpen={isChatOpen}
            className="size-[200px] md:size-[300px]"
          />
          {/* Pulsing glow behind the orb */}
          <div className="pointer-events-none absolute inset-0 rounded-full bg-blue-500 opacity-20 blur-[80px] transition-opacity duration-700 group-hover:opacity-40"></div>

          <div className="absolute -bottom-16 w-full text-center text-xs font-light tracking-widest opacity-40">
            {session.state === 'connected' ? 'LISTENING...' : 'CLICK ORB TO BEGIN'}
          </div>
        </div>
      </div>

      {/* Bottom Controls Area */}
      <motion.div
        className="absolute bottom-0 z-20 flex w-full flex-col items-center space-y-6 pb-8"
        {...BOTTOM_VIEW_MOTION_PROPS}
      >
        {/* Chat Transcript Overlay (if open) */}
        <AnimatePresence>
          {isChatOpen && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="mb-4 h-[40vh] w-full max-w-2xl px-4 flex flex-col"
            >
              <ChatTranscript messages={messages} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Feature Pills */}
        <div className="mb-4 flex max-w-3xl flex-wrap justify-center gap-3 px-4">
          <FeaturePill icon="🎤" label="Voice Control" />
          <FeaturePill icon="🎵" label="Spotify" />
          <FeaturePill icon="🌐" label="Web Search" />
          <FeaturePill icon="✉️" label="Email" />
          <FeaturePill icon="📊" label="Sheets" />
          <FeaturePill icon="💻" label="System" />
        </div>

        {/* LiveKit Control Bar */}
        <div className="rounded-full border border-white/10 bg-black/40 px-6 py-3 shadow-2xl backdrop-blur-xl">
          <AgentControlBar
            variant="livekit"
            isChatOpen={isChatOpen}
            onChatToggle={() => setIsChatOpen(!isChatOpen)}
            onDisconnect={onDisconnect}
            controls={{
              leave: true,
              microphone: true,
              screenShare: true,
              camera: true,
              chat: true,
            }}
            className="border-none bg-transparent shadow-none [&>button]:text-white/70 hover:[&>button]:text-white"
          />
        </div>

        <div className="text-xs font-light tracking-widest text-white/30 uppercase">
          Nivora • built by <span className="text-white/50">Anbalagan</span>
        </div>
      </motion.div>
    </div>
  );
}

function FeaturePill({ icon, label }: { icon: string; label: string }) {
  return (
    <div className="flex cursor-pointer items-center space-x-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 transition-all duration-300 hover:bg-white/10">
      <span className="opacity-70">{icon}</span>
      <span className="text-sm font-light tracking-wide opacity-80">{label}</span>
    </div>
  );
}
