import { motion } from 'framer-motion'
import { useState } from 'react'

interface WelcomeViewProps {
  onConnect: () => void
}

export function WelcomeView({ onConnect }: WelcomeViewProps) {
  const [isConnecting, setIsConnecting] = useState(false)
  const [permissionError, setPermissionError] = useState<string | null>(null)

  const handleConnect = async () => {
    setIsConnecting(true)
    setPermissionError(null)

    try {
      // Request microphone permission first
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true
      })

      // Stop the test stream
      stream.getTracks().forEach(track => track.stop())

      // Now proceed with connection
      onConnect()
    } catch (error) {
      console.error('Permission error:', error)
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          setPermissionError('Microphone access denied. Please allow microphone access and try again.')
        } else if (error.name === 'NotFoundError') {
          setPermissionError('No microphone found. Please connect a microphone and try again.')
        } else {
          setPermissionError(`Permission error: ${error.message}`)
        }
      } else {
        setPermissionError('Unknown permission error occurred.')
      }
      setIsConnecting(false)
    }
  }

  return (
    <div className="flex h-full w-full flex-col items-center justify-center p-6">
      {/* Logo */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="mb-6"
      >
        <div className="relative flex h-24 w-24 items-center justify-center">
          {/* Glow effect */}
          <div
            className="absolute inset-[-10px] rounded-full animate-pulse"
            style={{
              background: 'radial-gradient(circle, rgba(45, 212, 191, 0.3) 0%, transparent 70%)',
            }}
          />
          {/* Logo circle */}
          <div
            className="relative flex h-20 w-20 items-center justify-center rounded-full"
            style={{
              background: 'linear-gradient(135deg, #2dd4bf 0%, #9333ea 100%)',
              boxShadow: '0 0 40px rgba(45, 212, 191, 0.4)',
            }}
          >
            <svg className="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 2a3 3 0 00-3 3v7a3 3 0 006 0V5a3 3 0 00-3-3z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 10v2a7 7 0 01-14 0v-2" />
              <line x1="12" y1="19" x2="12" y2="22" stroke="currentColor" strokeWidth={2} />
            </svg>
          </div>
        </div>
      </motion.div>

      {/* Title */}
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="aurora-text mb-2 text-3xl font-light"
      >
        Nivora
      </motion.h1>

      {/* Subtitle */}
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="mb-8 text-sm text-muted-foreground"
      >
        Your AI companion, codenamed Friday
      </motion.p>

      {/* Error message */}
      {permissionError && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4 p-3 bg-red-900/20 border border-red-500/30 rounded-lg text-red-400 text-sm text-center max-w-sm"
        >
          {permissionError}
        </motion.div>
      )}

      {/* Connect Button */}
      <motion.button
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        onClick={handleConnect}
        disabled={isConnecting}
        className="group relative overflow-hidden rounded-full px-8 py-3 font-medium text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        style={{
          background: isConnecting
            ? 'linear-gradient(135deg, #6B7280 0%, #4B5563 100%)'
            : 'linear-gradient(135deg, #00BFFF 0%, #1E90FF 50%, #00CED1 100%)',
          boxShadow: isConnecting
            ? '0 0 20px rgba(107, 114, 128, 0.4)'
            : '0 0 20px rgba(0, 191, 255, 0.4)',
        }}
        whileHover={!isConnecting ? {
          scale: 1.05,
          boxShadow: '0 0 30px rgba(0, 191, 255, 0.6)',
        } : {}}
        whileTap={!isConnecting ? { scale: 0.98 } : {}}
      >
        <span className="relative z-10 text-sm font-bold tracking-wider uppercase">
          {isConnecting ? 'Connecting...' : 'Wanna Talk?'}
        </span>
      </motion.button>

      {/* Footer */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="mt-8 text-xs text-muted-foreground/50"
      >
        Powered by LiveKit
      </motion.p>

      {/* Permission tip */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="mt-4 text-xs text-muted-foreground/30 text-center max-w-xs"
      >
        Make sure to allow microphone access when prompted
      </motion.p>
    </div>
  )
}
