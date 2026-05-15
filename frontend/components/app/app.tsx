'use client';

import { memo, useCallback, useMemo } from 'react';
import { TokenSource } from 'livekit-client';
import { useSession } from '@livekit/components-react';
import { WarningIcon } from '@phosphor-icons/react/dist/ssr';
import type { AppConfig } from '@/app-config';
import { AgentSessionProvider } from '@/components/agents-ui/agent-session-provider';
import { StartAudioButton } from '@/components/agents-ui/start-audio-button';
import { ViewController } from '@/components/app/view-controller';
import { Toaster } from '@/components/ui/sonner';
import { useAgentErrors } from '@/hooks/useAgentErrors';
import { useDebugMode } from '@/hooks/useDebug';
import { getSandboxTokenSource } from '@/lib/utils';

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';

// Memoized setup component to prevent unnecessary re-renders
const AppSetup = memo(function AppSetup() {
  useDebugMode({ enabled: IN_DEVELOPMENT });
  useAgentErrors();
  return null;
});

// Memoized toaster styles
const TOASTER_STYLES = {
  '--normal-bg': 'var(--popover)',
  '--normal-text': 'var(--popover-foreground)',
  '--normal-border': 'var(--border)',
} as React.CSSProperties;

// Memoized warning icon
const WarningIconMemo = memo(function WarningIconMemo() {
  return <WarningIcon weight="bold" />;
});

interface AppProps {
  appConfig: AppConfig;
}

export const App = memo(function App({ appConfig }: AppProps) {
  // Memoize token source to prevent recreation on every render
  const tokenSource = useMemo(() => {
    return typeof process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT === 'string'
      ? getSandboxTokenSource(appConfig)
      : TokenSource.endpoint('/api/connection-details');
  }, [appConfig]);

  // Memoize session options to prevent recreation
  const sessionOptions = useMemo(() => {
    return appConfig.agentName ? { agentName: appConfig.agentName } : undefined;
  }, [appConfig.agentName]);

  const session = useSession(tokenSource, sessionOptions);

  // Memoize start audio button label
  const startAudioLabel = useMemo(() => 'Start Audio', []);

  return (
    <AgentSessionProvider session={session}>
      <AppSetup />
      <main className="grid h-svh grid-cols-1 place-content-center">
        <ViewController appConfig={appConfig} />
      </main>
      <StartAudioButton label={startAudioLabel} />
      <Toaster
        icons={{
          warning: <WarningIconMemo />,
        }}
        position="top-center"
        className="toaster group"
        style={TOASTER_STYLES}
      />
    </AgentSessionProvider>
  );
});
