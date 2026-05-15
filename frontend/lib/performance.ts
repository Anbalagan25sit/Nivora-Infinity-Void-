import React from 'react';

/**
 * Performance utilities for monitoring and optimizing the Nivora Frontend
 */

export interface PerformanceMetrics {
  fps: number;
  memoryUsage: number;
  renderTime: number;
  domNodes: number;
  eventListeners: number;
}

export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private frameCount = 0;
  private lastTime = 0;
  private fps = 0;
  private rafId: number | null = null;

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  startMonitoring(): void {
    if (typeof window === 'undefined') return;

    const monitor = (timestamp: number) => {
      this.frameCount++;

      if (timestamp - this.lastTime >= 1000) {
        this.fps = Math.round((this.frameCount * 1000) / (timestamp - this.lastTime));
        this.frameCount = 0;
        this.lastTime = timestamp;

        // Log performance warnings in development
        if (process.env.NODE_ENV === 'development') {
          if (this.fps < 30) {
            console.warn(`🐌 Low FPS detected: ${this.fps}fps`);
          }

          const metrics = this.getMetrics();
          if (metrics.memoryUsage > 50) {
            console.warn(`🧠 High memory usage: ${metrics.memoryUsage}MB`);
          }
        }
      }

      this.rafId = requestAnimationFrame(monitor);
    };

    this.rafId = requestAnimationFrame(monitor);
  }

  stopMonitoring(): void {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }

  getMetrics(): PerformanceMetrics {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const memory = (performance as any)?.memory;
    const navigation = performance?.getEntriesByType?.(
      'navigation'
    )?.[0] as PerformanceNavigationTiming;

    return {
      fps: this.fps,
      memoryUsage: memory ? Math.round(memory.usedJSHeapSize / 1024 / 1024) : 0,
      renderTime: navigation ? navigation.loadEventEnd - navigation.loadEventStart : 0,
      domNodes: document.querySelectorAll('*').length,
      eventListeners: this.countEventListeners(),
    };
  }

  private countEventListeners(): number {
    // Approximate event listener count
    return document.querySelectorAll('[onclick], [onload], [onchange]').length;
  }
}

// React hook for performance monitoring
export function usePerformanceMonitor() {
  const [metrics, setMetrics] = React.useState<PerformanceMetrics | null>(null);

  React.useEffect(() => {
    if (typeof window === 'undefined') return;

    const monitor = PerformanceMonitor.getInstance();
    monitor.startMonitoring();

    // Update metrics every 2 seconds
    const interval = setInterval(() => {
      setMetrics(monitor.getMetrics());
    }, 2000);

    return () => {
      monitor.stopMonitoring();
      clearInterval(interval);
    };
  }, []);

  return metrics;
}

// Performance optimization utilities
export const performanceUtils = {
  // Debounce function for expensive operations
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): (...args: Parameters<T>) => void {
    let timeout: NodeJS.Timeout;
    return function executedFunction(...args: Parameters<T>) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Throttle function for frequent events
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  throttle<T extends (...args: any[]) => any>(
    func: T,
    limit: number
  ): (...args: Parameters<T>) => void {
    let inThrottle: boolean;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return function executedFunction(this: any, ...args: Parameters<T>) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => (inThrottle = false), limit);
      }
    };
  },

  // Memory cleanup utility
  cleanupMemory(): void {
    // Force garbage collection if available (Chrome DevTools)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    if ((window as any).gc) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (window as any).gc();
    }
  },

  // Preload critical resources
  preloadResource(url: string, as: string = 'script'): void {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = url;
    link.as = as;
    document.head.appendChild(link);
  },

  // Lazy load images with intersection observer
  lazyLoadImages(): void {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement;
          img.src = img.dataset.src || '';
          img.classList.remove('lazy');
          observer.unobserve(img);
        }
      });
    });

    document.querySelectorAll('img[data-src]').forEach((img) => {
      imageObserver.observe(img);
    });
  },

  // Optimize bundle size by removing unused dependencies
  analyzeBundle(): void {
    if (process.env.NODE_ENV === 'development') {
      console.log('📦 Bundle analysis available at /_next/bundle-analyzer');
    }
  },
};

// CSS-in-JS optimization
export const optimizedStyles = {
  // Commonly used styles as objects to prevent recreation
  flexCenter: { display: 'flex', alignItems: 'center', justifyContent: 'center' },
  absoluteFull: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 },
  visuallyHidden: {
    position: 'absolute',
    width: '1px',
    height: '1px',
    padding: 0,
    margin: '-1px',
    overflow: 'hidden',
    clip: 'rect(0, 0, 0, 0)',
    whiteSpace: 'nowrap',
    border: 0,
  },
} as const;
