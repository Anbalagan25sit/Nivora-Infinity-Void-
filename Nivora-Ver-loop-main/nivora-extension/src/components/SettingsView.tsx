import { useState } from 'react'

interface Config {
  livekitUrl: string
  apiEndpoint: string
}

interface SettingsViewProps {
  config: Config
  onSave: (config: Config) => void
  onCancel: () => void
}

export function SettingsView({ config, onSave, onCancel }: SettingsViewProps) {
  const [livekitUrl, setLivekitUrl] = useState(config.livekitUrl)
  const [apiEndpoint, setApiEndpoint] = useState(config.apiEndpoint)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)

  const handleTest = async () => {
    setTesting(true)
    setTestResult(null)

    try {
      const response = await fetch(`${apiEndpoint}?room=test&participant=test-user`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      if (data.token) {
        setTestResult({ success: true, message: 'Connection successful!' })
      } else {
        setTestResult({ success: false, message: 'No token received' })
      }
    } catch (error: any) {
      setTestResult({ success: false, message: `Failed: ${error.message}` })
    } finally {
      setTesting(false)
    }
  }

  const handleSave = () => {
    onSave({ livekitUrl, apiEndpoint })
  }

  return (
    <div className="flex h-full w-full flex-col bg-background p-6">
      <h1 className="mb-6 text-xl font-semibold">Settings</h1>

      <div className="space-y-4">
        <div>
          <label className="mb-2 block text-sm text-muted-foreground">
            LiveKit Server URL
          </label>
          <input
            type="text"
            value={livekitUrl}
            onChange={(e) => setLivekitUrl(e.target.value)}
            placeholder="wss://your-server.livekit.cloud"
            className="w-full rounded-lg bg-muted px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-primary/50"
          />
        </div>

        <div>
          <label className="mb-2 block text-sm text-muted-foreground">
            Token API Endpoint
          </label>
          <input
            type="text"
            value={apiEndpoint}
            onChange={(e) => setApiEndpoint(e.target.value)}
            placeholder="http://localhost:8080/api/token"
            className="w-full rounded-lg bg-muted px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-primary/50"
          />
        </div>

        {/* Test Result */}
        {testResult && (
          <div
            className={`rounded-lg p-3 text-sm ${
              testResult.success
                ? 'bg-green-500/20 text-green-400'
                : 'bg-destructive/20 text-destructive'
            }`}
          >
            {testResult.message}
          </div>
        )}
      </div>

      <div className="mt-auto space-y-3 pt-6">
        <button
          onClick={handleTest}
          disabled={testing}
          className="w-full rounded-lg bg-muted py-3 text-sm font-medium hover:bg-muted/80 disabled:opacity-50"
        >
          {testing ? 'Testing...' : 'Test Connection'}
        </button>

        <button
          onClick={handleSave}
          className="w-full rounded-lg bg-primary py-3 text-sm font-medium text-background hover:bg-primary-hover"
        >
          Save Settings
        </button>

        <button
          onClick={onCancel}
          className="w-full rounded-lg py-3 text-sm text-muted-foreground hover:text-foreground"
        >
          Cancel
        </button>
      </div>

      <div className="mt-4 rounded-lg bg-muted/50 p-3">
        <p className="text-xs text-muted-foreground">
          <strong>Quick Tips:</strong>
          <br />• Press <code className="rounded bg-muted px-1">Alt+N</code> to open
          <br />• Token server must be running on port 8080
          <br />• Make sure Nivora agent is running
        </p>
      </div>
    </div>
  )
}
