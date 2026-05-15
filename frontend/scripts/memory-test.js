#!/usr/bin/env node

/**
 * Memory and Performance Testing Script for Nivora Frontend
 * Run with: node --expose-gc scripts/memory-test.js
 */

const fs = require('fs');
const path = require('path');

class PerformanceProfiler {
  constructor() {
    this.metrics = {
      initialMemory: 0,
      peakMemory: 0,
      currentMemory: 0,
      gcCollections: 0,
      startTime: 0,
      testResults: [],
    };
  }

  async profileMemoryUsage() {
    console.log('🧠 Starting Memory Usage Profiling...\n');

    this.metrics.startTime = Date.now();
    this.metrics.initialMemory = this.getMemoryUsage();

    console.log(`Initial Memory: ${this.formatMemory(this.metrics.initialMemory)}`);

    // Simulate heavy component mounting/unmounting
    await this.simulateComponentLifecycle();

    // Simulate heavy animation cycles
    await this.simulateAnimations();

    // Simulate LiveKit session management
    await this.simulateLiveKitSession();

    this.generateReport();
  }

  async simulateComponentLifecycle() {
    console.log('🔄 Testing Component Lifecycle...');

    // Simulate mounting 100 heavy components
    const components = [];
    for (let i = 0; i < 100; i++) {
      components.push(this.createMockComponent());

      if (i % 20 === 0) {
        this.trackMemory('Component Mount', i);
        await this.sleep(10);
      }
    }

    // Cleanup components
    for (let i = 0; i < components.length; i++) {
      components[i] = null;

      if (i % 20 === 0) {
        this.forceGC();
        this.trackMemory('Component Cleanup', i);
        await this.sleep(10);
      }
    }
  }

  async simulateAnimations() {
    console.log('🎬 Testing Animation Performance...');

    // Simulate 50 concurrent animations
    const animations = [];
    for (let i = 0; i < 50; i++) {
      animations.push(this.createMockAnimation());
    }

    this.trackMemory('Peak Animations', 50);

    // Cleanup animations
    animations.forEach((anim, i) => {
      clearInterval(anim);
      if (i % 10 === 0) {
        this.forceGC();
      }
    });

    this.trackMemory('Post-Animation Cleanup', 0);
  }

  async simulateLiveKitSession() {
    console.log('📡 Testing LiveKit Session Simulation...');

    // Simulate audio/video streams
    const audioBuffer = new ArrayBuffer(1024 * 1024); // 1MB
    const videoBuffer = new ArrayBuffer(5 * 1024 * 1024); // 5MB

    this.trackMemory('LiveKit Buffers Created', 0);

    // Simulate processing
    await this.sleep(500);

    // Cleanup
    audioBuffer && this.forceGC();
    videoBuffer && this.forceGC();

    this.trackMemory('LiveKit Cleanup', 0);
  }

  createMockComponent() {
    return {
      id: Math.random(),
      data: new Array(1000).fill(0).map(() => Math.random()),
      handlers: {
        onClick: () => {},
        onHover: () => {},
        onFocus: () => {},
      },
    };
  }

  createMockAnimation() {
    let frame = 0;
    return setInterval(() => {
      frame++;
      // Simulate DOM manipulation
      if (frame % 60 === 0) {
        this.trackMemory('Animation Frame', frame);
      }
    }, 16); // ~60fps
  }

  getMemoryUsage() {
    if (process.memoryUsage) {
      const usage = process.memoryUsage();
      return usage.heapUsed;
    }
    return 0;
  }

  formatMemory(bytes) {
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  }

  trackMemory(label, value) {
    const currentMemory = this.getMemoryUsage();
    const timestamp = Date.now() - this.metrics.startTime;

    if (currentMemory > this.metrics.peakMemory) {
      this.metrics.peakMemory = currentMemory;
    }

    this.metrics.testResults.push({
      label,
      value,
      memory: currentMemory,
      timestamp,
      formatted: this.formatMemory(currentMemory),
    });

    console.log(`  ${label} (${value}): ${this.formatMemory(currentMemory)}`);
  }

  forceGC() {
    if (global.gc) {
      global.gc();
      this.metrics.gcCollections++;
    }
  }

  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  generateReport() {
    const finalMemory = this.getMemoryUsage();
    const totalTime = Date.now() - this.metrics.startTime;
    const memoryLeak = finalMemory - this.metrics.initialMemory;

    console.log('\n📊 PERFORMANCE REPORT');
    console.log('================================');
    console.log(`Total Test Time: ${totalTime}ms`);
    console.log(`Initial Memory: ${this.formatMemory(this.metrics.initialMemory)}`);
    console.log(`Peak Memory: ${this.formatMemory(this.metrics.peakMemory)}`);
    console.log(`Final Memory: ${this.formatMemory(finalMemory)}`);
    console.log(`Memory Difference: ${this.formatMemory(memoryLeak)}`);
    console.log(`GC Collections: ${this.metrics.gcCollections}`);

    // Memory leak analysis
    if (memoryLeak > 10 * 1024 * 1024) {
      // 10MB
      console.log('⚠️  POTENTIAL MEMORY LEAK DETECTED!');
    } else if (memoryLeak > 5 * 1024 * 1024) {
      // 5MB
      console.log('⚠️  Elevated memory usage detected');
    } else {
      console.log('✅ Memory usage looks healthy');
    }

    // Peak memory analysis
    if (this.metrics.peakMemory > 100 * 1024 * 1024) {
      // 100MB
      console.log('⚠️  High peak memory usage detected');
    } else {
      console.log('✅ Peak memory usage within acceptable range');
    }

    // Save detailed report
    this.saveDetailedReport({
      summary: {
        totalTime,
        initialMemory: this.metrics.initialMemory,
        peakMemory: this.metrics.peakMemory,
        finalMemory,
        memoryLeak,
        gcCollections: this.metrics.gcCollections,
      },
      detailed: this.metrics.testResults,
      timestamp: new Date().toISOString(),
    });
  }

  saveDetailedReport(report) {
    const reportPath = path.join(process.cwd(), 'performance-report.json');

    try {
      fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
      console.log(`\n📄 Detailed report saved to: ${reportPath}`);
    } catch (error) {
      console.error('Failed to save report:', error.message);
    }
  }
}

// Run the profiler
async function main() {
  console.log('🚀 Nivora Frontend Performance Profiler\n');

  if (!global.gc) {
    console.log(
      '⚠️  Warning: Garbage collection not exposed. Run with --expose-gc for better results.\n'
    );
  }

  const profiler = new PerformanceProfiler();
  await profiler.profileMemoryUsage();

  console.log('\n🎉 Profiling complete!');
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = PerformanceProfiler;
