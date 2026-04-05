import { useMemo, useState, useEffect } from 'react'
import { TokenSource } from 'livekit-client'
import {
  useSession,
  useSessionContext,
  useVoiceAssistant,
  SessionProvider,
  RoomAudioRenderer,
} from '@livekit/components-react'
import { PlaygroundView } from './components/PlaygroundView'
import { WelcomeView } from './components/WelcomeView'
import { SettingsView } from './components/SettingsView'

// Config stored in chrome.storage
interface Config {
  livekitUrl: string
  apiEndpoint: string
}

const DEFAULT_CONFIG: Config = {
  livekitUrl: 'wss://nivora-5opea2lo.livekit.cloud',
  apiEndpoint: 'http://localhost:8080/api/token',
}

function AgentSessionProvider({
  session,
  children
}: {
  session: ReturnType<typeof useSession>
  children: React.ReactNode
}) {
  return (
    <SessionProvider session={session}>
      {children}
      <RoomAudioRenderer />
    </SessionProvider>
  )
}

function AppContent() {
  const session = useSessionContext()
  const { isConnected } = session

  if (!isConnected) {
    return <WelcomeView onConnect={session.start} />
  }

  return <PlaygroundView />
}

export default function App() {
  const [config, setConfig] = useState<Config>(DEFAULT_CONFIG)
  const [showSettings, setShowSettings] = useState(false)
  const [configLoaded, setConfigLoaded] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load config from chrome.storage
  useEffect(() => {
    if (typeof chrome !== 'undefined' && chrome.storage) {
      chrome.storage.sync.get(['livekitUrl', 'apiEndpoint'], (result) => {
        if (result.livekitUrl || result.apiEndpoint) {
          setConfig({
            livekitUrl: result.livekitUrl || DEFAULT_CONFIG.livekitUrl,
            apiEndpoint: result.apiEndpoint || DEFAULT_CONFIG.apiEndpoint,
          })
        }
        setConfigLoaded(true)
      })
    } else {
      setConfigLoaded(true)
    }
  }, [])

  // Create token source with better error handling
  const tokenSource = useMemo(() => {
    if (!configLoaded) return null

    return TokenSource.custom(async () => {
      try {
        const participantId = 'user-' + Math.random().toString(36).substr(2, 9)

        // Add console logging for debugging
        console.log('Fetching token from:', `${config.apiEndpoint}?room=nivora-assistant&participant=${participantId}`)

        const response = await fetch(
          `${config.apiEndpoint}?room=nivora-assistant&participant=${participantId}`,
          {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          }
        )

        if (!response.ok) {
          throw new Error(`Token server error: ${response.status} ${response.statusText}`)
        }

        const data = await response.json()
        console.log('Token response:', data)

        if (!data.token) {
          throw new Error('No token received from server')
        }

        return {
          serverUrl: config.livekitUrl,
          roomName: data.room || 'nivora-assistant',
          participantToken: data.token,
          participantName: data.participant || participantId,
        }
      } catch (error) {
        console.error('Token fetch error:', error)
        setError(error instanceof Error ? error.message : 'Unknown error')
        throw error
      }
    })
  }, [config, configLoaded])

  // Only create session if tokenSource is available
  const session = useSession(tokenSource || undefined)

  const handleSaveSettings = (newConfig: Config) => {
    setConfig(newConfig)
    if (typeof chrome !== 'undefined' && chrome.storage) {
      chrome.storage.sync.set(newConfig)
    }
    setShowSettings(false)
    setError(null) // Clear any previous errors
  }

  if (!configLoaded) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-background">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-screen w-full flex-col items-center justify-center bg-background p-6">
        <div className="text-red-400 mb-4">Connection Error</div>
        <div className="text-sm text-muted-foreground text-center mb-4">{error}</div>
        <button
          onClick={() => setError(null)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Retry
        </button>
        <button
          onClick={() => setShowSettings(true)}
          className="mt-2 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
        >
          Settings
        </button>
      </div>
    )
  }

  if (showSettings) {
    return (
      <SettingsView
        config={config}
        onSave={handleSaveSettings}
        onCancel={() => setShowSettings(false)}
      />
    )
  }

  if (!tokenSource) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-background">
        <div className="text-muted-foreground">Initializing...</div>
      </div>
    )
  }

  return (
    <div className="relative h-screen w-full overflow-hidden bg-background">
      {/* Settings button */}
      <button
        onClick={() => setShowSettings(true)}
        className="absolute right-4 top-4 z-50 rounded-full p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
        title="Settings"
      >
        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </button>

      <AgentSessionProvider session={session}>
        <AppContent />
      </AgentSessionProvider>
    </div>
  )
}
