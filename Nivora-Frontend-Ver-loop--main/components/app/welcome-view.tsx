'use client';

import React, { forwardRef } from 'react';
import { LandingPage } from '@/components/app/landing-page';

// -----------------------------------------------------------------------------
// COMPONENT
// -----------------------------------------------------------------------------

interface WelcomeViewProps {
  startButtonText?: string;
  onStartCall: () => void;
}

export const WelcomeView = forwardRef<HTMLDivElement, WelcomeViewProps & React.ComponentProps<'div'>>(
  ({ onStartCall, ...props }, ref) => {
    const { className, style, ...rest } = props;

    return (
      <div 
        ref={ref} 
        className={className || ''} 
        style={style}
        {...rest}
      >
        <LandingPage onStartCall={onStartCall} />
      </div>
    );
  }
);

WelcomeView.displayName = 'WelcomeView';