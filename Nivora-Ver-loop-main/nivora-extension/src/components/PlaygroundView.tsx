import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  useSessionContext,
  useSessionMessages,
  useVoiceAssistant,
  useMultibandTrackVolume,
  useChat,
} from '@livekit/components-react'
import { Track } from 'livekit-client'
import { cn } from '@/lib/utils'

export function PlaygroundView() {
  const session = useSessionContext()
  const { messages } = useSessionMessages(session)
  const { state, audioTrack } = useVoiceAssistant()
  const { send } = useChat()
  const [chatOpen, setChatOpen] = useState(false)
  const [message, setMessage] = useState('')
  const transcriptRef = useRef<HTMLDivElement>(null)

  // Auto-scroll transcript
  useEffect(() => {
    if (transcriptRef.current) {
      transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight
    }
  }, [messages])

  const handleSendMessage = async () => {
    if (!message.trim()) return
    await send(message.trim())
    setMessage('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex h-full w-full flex-col">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border/40 px-4 py-3">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/20">
            <span className="text-xs font-bold text-primary">N</span>
          </div>
          <h1 className="text-sm font-semibold">Nivora Assistant</h1>
        </div>
        <ConnectionStatus state={state} />
      </header>

      {/* Main Content */}
      <div className="flex flex-1 flex-col items-center justify-center overflow-hidden p-4">
        {/* Visualizer */}
        <div className="mb-4">
          <AudioVisualizer state={state} audioTrack={audioTrack} />
        </div>

        {/* Status */}
        <p className="mb-4 text-xs text-muted-foreground">
          {state === 'speaking' && 'Nivora is speaking...'}
          {state === 'listening' && 'Listening...'}
          {state === 'thinking' && 'Thinking...'}
          {state === 'connecting' && 'Connecting...'}
          {state === 'idle' && 'Ready'}
        </p>

        {/* Last message */}
        {messages.length > 0 && (
          <div className="w-full max-w-sm rounded-lg bg-muted/50 p-3 text-center">
            <p className="text-xs text-muted-foreground">
              {messages[messages.length - 1]?.from?.isLocal ? 'You' : 'Nivora'}
            </p>
            <p className="text-sm">{messages[messages.length - 1]?.message}</p>
          </div>
        )}
      </div>

      {/* Transcript Panel */}
      <AnimatePresence>
        {chatOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 200, opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-border/40 overflow-hidden"
          >
            <div
              ref={transcriptRef}
              className="h-full overflow-y-auto p-3 space-y-2"
            >
              {messages.length === 0 ? (
                <p className="text-center text-xs text-muted-foreground">
                  No messages yet
                </p>
              ) : (
                messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={cn(
                      'rounded-lg p-2 text-sm',
                      msg.from?.isLocal
                        ? 'ml-auto max-w-[80%] bg-primary text-background'
                        : 'mr-auto max-w-[80%] bg-muted'
                    )}
                  >
                    {msg.message}
                  </div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Controls */}
      <div className="border-t border-border/40 p-3">
        {/* Chat Input */}
        <AnimatePresence>
          {chatOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="mb-3 overflow-hidden"
            >
              <div className="flex gap-2">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type a message..."
                  className="flex-1 rounded-full bg-muted px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/50"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!message.trim()}
                  className="rounded-full bg-primary px-4 py-2 text-sm font-medium text-background disabled:opacity-50"
                >
                  Send
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Control Buttons */}
        <div className="flex items-center justify-center gap-2">
          <MicrophoneButton />
          <button
            onClick={() => setChatOpen(!chatOpen)}
            className={cn(
              'rounded-full p-3 transition-colors',
              chatOpen ? 'bg-primary text-background' : 'bg-muted hover:bg-muted/80'
            )}
            title="Toggle chat"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </button>
          <button
            onClick={() => session.end()}
            className="rounded-full bg-destructive/20 p-3 text-destructive hover:bg-destructive/30 transition-colors"
            title="End session"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M5 3a2 2 0 00-2 2v1c0 8.284 6.716 15 15 15h1a2 2 0 002-2v-3.28a1 1 0 00-.684-.948l-4.493-1.498a1 1 0 00-1.21.502l-1.13 2.257a11.042 11.042 0 01-5.516-5.517l2.257-1.128a1 1 0 00.502-1.21L9.228 3.683A1 1 0 008.279 3H5z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

// Audio Visualizer Component
function AudioVisualizer({
  state,
  audioTrack,
}: {
  state: string
  audioTrack: any
}) {
  const volumeBands = useMultibandTrackVolume(audioTrack, {
    bands: 5,
    loPass: 100,
    hiPass: 200,
  })

  const bands = state === 'speaking' ? volumeBands : new Array(5).fill(0.1)

  return (
    <div className="flex h-32 w-48 items-end justify-center gap-2">
      {bands.map((band: number, idx: number) => (
        <motion.div
          key={idx}
          className={cn(
            'w-6 rounded-full',
            state === 'speaking' ? 'bg-primary' : 'bg-muted-foreground/30'
          )}
          animate={{
            height: `${Math.max(20, band * 100)}%`,
            backgroundColor:
              state === 'speaking'
                ? '#2dd4bf'
                : state === 'thinking'
                ? '#9333ea'
                : '#71717a',
          }}
          transition={{ duration: 0.1 }}
        />
      ))}
    </div>
  )
}

// Connection Status
function ConnectionStatus({ state }: { state: string }) {
  const isActive = state !== 'idle' && state !== 'connecting'

  return (
    <div className="flex items-center gap-2">
      <div
        className={cn(
          'h-2 w-2 rounded-full',
          isActive ? 'bg-green-500' : 'bg-yellow-500'
        )}
      />
      <span className="text-xs text-muted-foreground capitalize">
        {state}
      </span>
    </div>
  )
}

// Microphone Button
function MicrophoneButton() {
  const [isMuted, setIsMuted] = useState(false)
  const session = useSessionContext()

  const handleToggle = async () => {
    const room = session.room
    if (!room) return

    const enabled = !isMuted
    await room.localParticipant.setMicrophoneEnabled(enabled)
    setIsMuted(!enabled)
  }

  return (
    <button
      onClick={handleToggle}
      className={cn(
        'rounded-full p-4 transition-all',
        isMuted
          ? 'bg-destructive text-white'
          : 'bg-primary text-background hover:bg-primary-hover'
      )}
      title={isMuted ? 'Unmute' : 'Mute'}
    >
      {isMuted ? (
        <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
        </svg>
      ) : (
        <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 2a3 3 0 00-3 3v7a3 3 0 006 0V5a3 3 0 00-3-3z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 10v2a7 7 0 01-14 0v-2" />
          <line x1="12" y1="19" x2="12" y2="22" stroke="currentColor" strokeWidth={2} />
        </svg>
      )}
    </button>
  )
}
