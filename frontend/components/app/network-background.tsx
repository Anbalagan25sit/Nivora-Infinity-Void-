'use client';

import { useEffect, useRef } from 'react';

// --- Perlin noise (simplex-like, self-contained) ---
function createNoise() {
  const p = new Uint8Array(512);
  const permutation = Array.from({ length: 256 }, (_, i) => i);
  for (let i = 255; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [permutation[i], permutation[j]] = [permutation[j], permutation[i]];
  }
  for (let i = 0; i < 512; i++) p[i] = permutation[i & 255];

  function fade(t: number) {
    return t * t * t * (t * (t * 6 - 15) + 10);
  }
  function lerp(a: number, b: number, t: number) {
    return a + t * (b - a);
  }
  function grad(hash: number, x: number, y: number) {
    const h = hash & 3;
    const u = h < 2 ? x : y;
    const v = h < 2 ? y : x;
    return (h & 1 ? -u : u) + (h & 2 ? -v : v);
  }

  return function noise(x: number, y: number): number {
    const X = Math.floor(x) & 255;
    const Y = Math.floor(y) & 255;
    x -= Math.floor(x);
    y -= Math.floor(y);
    const u = fade(x),
      v = fade(y);
    const a = p[X] + Y,
      b = p[X + 1] + Y;
    return lerp(
      lerp(grad(p[a], x, y), grad(p[b], x - 1, y), u),
      lerp(grad(p[a + 1], x, y - 1), grad(p[b + 1], x - 1, y - 1), u),
      v
    );
  };
}

// Color palette
const COLORS = ['#00E5FF', '#7F00FF', '#4B0082', '#00BFFF', '#9400D3'];

interface Node {
  x: number;
  y: number;
  baseX: number;
  baseY: number;
  noiseOffsetX: number;
  noiseOffsetY: number;
  color: string;
  radius: number;
  pulsePhase: number;
}

export function NetworkBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const noise = createNoise();
    let animFrameId: number;
    let time = 0;

    const NODE_COUNT = 55;
    const MAX_DIST = 200;
    const NOISE_SPEED = 0.0003;
    const NOISE_SCALE = 1.8;
    const DRIFT_AMOUNT = 60;

    let nodes: Node[] = [];

    function resize() {
      canvas!.width = window.innerWidth;
      canvas!.height = window.innerHeight;
      initNodes();
    }

    function initNodes() {
      nodes = Array.from({ length: NODE_COUNT }, (_, i) => {
        const x = Math.random() * canvas!.width;
        const y = Math.random() * canvas!.height;
        return {
          x,
          y,
          baseX: x,
          baseY: y,
          noiseOffsetX: Math.random() * 1000,
          noiseOffsetY: Math.random() * 1000,
          color: COLORS[i % COLORS.length],
          radius: 1.5 + Math.random() * 2,
          pulsePhase: Math.random() * Math.PI * 2,
        };
      });
    }

    function hexToRgb(hex: string) {
      const r = parseInt(hex.slice(1, 3), 16);
      const g = parseInt(hex.slice(3, 5), 16);
      const b = parseInt(hex.slice(5, 7), 16);
      return { r, g, b };
    }

    function drawGlowDot(node: Node, pulse: number) {
      const { r, g, b } = hexToRgb(node.color);
      const glowRadius = node.radius * (2.5 + pulse);

      const gradient = ctx!.createRadialGradient(node.x, node.y, 0, node.x, node.y, glowRadius * 4);
      gradient.addColorStop(0, `rgba(${r},${g},${b},0.9)`);
      gradient.addColorStop(0.3, `rgba(${r},${g},${b},0.4)`);
      gradient.addColorStop(1, `rgba(${r},${g},${b},0)`);

      ctx!.beginPath();
      ctx!.arc(node.x, node.y, glowRadius * 4, 0, Math.PI * 2);
      ctx!.fillStyle = gradient;
      ctx!.fill();

      ctx!.beginPath();
      ctx!.arc(node.x, node.y, node.radius + pulse * 0.5, 0, Math.PI * 2);
      ctx!.fillStyle = `rgba(${r},${g},${b},1)`;
      ctx!.shadowColor = node.color;
      ctx!.shadowBlur = 12;
      ctx!.fill();
      ctx!.shadowBlur = 0;
    }

    function drawLine(a: Node, b: Node, dist: number) {
      const opacity = Math.pow(1 - dist / MAX_DIST, 2) * 0.7;
      const { r: r1, g: g1, b: b1 } = hexToRgb(a.color);
      const { r: r2, g: g2, b: b2 } = hexToRgb(b.color);

      const grad = ctx!.createLinearGradient(a.x, a.y, b.x, b.y);
      grad.addColorStop(0, `rgba(${r1},${g1},${b1},${opacity})`);
      grad.addColorStop(1, `rgba(${r2},${g2},${b2},${opacity})`);

      ctx!.beginPath();
      ctx!.moveTo(a.x, a.y);
      ctx!.lineTo(b.x, b.y);
      ctx!.strokeStyle = grad;
      ctx!.lineWidth = 0.6 + opacity * 0.8;
      ctx!.shadowColor = a.color;
      ctx!.shadowBlur = 6;
      ctx!.stroke();
      ctx!.shadowBlur = 0;
    }

    function draw() {
      time += 1;

      // Background gradient
      const bg = ctx!.createRadialGradient(
        canvas!.width / 2,
        canvas!.height / 2,
        0,
        canvas!.width / 2,
        canvas!.height / 2,
        Math.max(canvas!.width, canvas!.height) * 0.75
      );
      bg.addColorStop(0, '#0d1526');
      bg.addColorStop(1, '#0A0F1C');
      ctx!.fillStyle = bg;
      ctx!.fillRect(0, 0, canvas!.width, canvas!.height);

      // Update node positions using Perlin noise
      nodes.forEach((node) => {
        const nx = noise(node.noiseOffsetX + time * NOISE_SPEED, node.noiseOffsetY) * NOISE_SCALE;
        const ny = noise(node.noiseOffsetX, node.noiseOffsetY + time * NOISE_SPEED) * NOISE_SCALE;
        node.x = node.baseX + nx * DRIFT_AMOUNT;
        node.y = node.baseY + ny * DRIFT_AMOUNT;
      });

      // Draw edges
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < MAX_DIST) {
            drawLine(nodes[i], nodes[j], dist);
          }
        }
      }

      // Draw nodes
      nodes.forEach((node) => {
        const pulse = Math.sin(time * 0.02 + node.pulsePhase) * 0.5 + 0.5;
        drawGlowDot(node, pulse);
      });

      animFrameId = requestAnimationFrame(draw);
    }

    resize();
    window.addEventListener('resize', resize);
    draw();

    return () => {
      cancelAnimationFrame(animFrameId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 -z-10 h-full w-full"
      style={{ background: '#0A0F1C' }}
    />
  );
}
