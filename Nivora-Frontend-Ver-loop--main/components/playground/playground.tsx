'use client';

import { useMemo } from 'react';
import { TokenSource } from 'livekit-client';
import { useSession } from '@livekit/components-react';
import { AgentSessionProvider } from '@/components/agents-ui/agent-session-provider';
import { StartAudioButton } from '@/components/agents-ui/start-audio-button';
import { PlaygroundView } from '@/components/playground/playground-view';
import { Toaster } from '@/components/ui/sonner';
import { useAgentErrors } from '@/hooks/useAgentErrors';
import { useDebugMode } from '@/hooks/useDebug';
import { WarningIcon } from '@phosphor-icons/react/dist/ssr';
import { getSandboxTokenSource } from '@/lib/utils';

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';

function AppSetup() {
  useDebugMode({ enabled: IN_DEVELOPMENT });
  useAgentErrors();

  return null;
}

export function Playground() {
  const tokenSource = useMemo(() => {
    return typeof process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT === 'string'
      ? getSandboxTokenSource({
          pageTitle: 'LiveKit Playground',
          pageDescription: 'Voice Assistant Playground',
          companyName: 'LiveKit',
          supportsChatInput: true,
          supportsVideoInput: false,
          supportsScreenShare: false,
          isPreConnectBufferEnabled: true,
          logo: '/livekit-logo.svg',
          startButtonText: 'Start Session',
        })
      : TokenSource.endpoint('/api/connection-details');
  }, []);

  const session = useSession(tokenSource);

  return (
    <AgentSessionProvider session={session}>
      <AppSetup />
      <main className="relative h-screen w-screen overflow-hidden bg-background">
        <PlaygroundView />
      </main>
      <StartAudioButton label="Start Audio" />
      <Toaster
        icons={{
          warning: <WarningIcon weight="bold" />,
        }}
        position="top-center"
        className="toaster group"
        style={
          {
            '--normal-bg': 'var(--popover)',
            '--normal-text': 'var(--popover-foreground)',
            '--normal-border': 'var(--border)',
          } as React.CSSProperties
        }
      />
    </AgentSessionProvider>
  );
}
