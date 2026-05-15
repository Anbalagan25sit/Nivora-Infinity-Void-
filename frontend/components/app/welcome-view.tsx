'use client';

import React, { forwardRef } from 'react';
import { LandingPage } from '@/components/app/landing-page';

// -----------------------------------------------------------------------------
// COMPONENT
// -----------------------------------------------------------------------------

interface WelcomeViewProps {
  onStartCall: () => void;
}

export const WelcomeView = forwardRef<
  HTMLDivElement,
  WelcomeViewProps & Omit<React.ComponentProps<'div'>, 'startButtonText'>
>(({ onStartCall, ...props }, ref) => {
  const { className, style, ...rest } = props;

  return (
    <div ref={ref} className={className || ''} style={style} {...rest}>
      <LandingPage onStartCall={onStartCall} />
    </div>
  );
});

WelcomeView.displayName = 'WelcomeView';
