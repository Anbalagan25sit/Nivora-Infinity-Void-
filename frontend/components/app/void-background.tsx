'use client';

import React, { useEffect, useRef } from 'react';

export function VoidBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let particles: {
      x: number;
      y: number;
      size: number;
      speedX: number;
      speedY: number;
      opacity: number;
      life: number;
      maxLife: number;
    }[] = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initParticles();
    };

    const initParticles = () => {
      particles = [];
      const numParticles = Math.floor((canvas.width * canvas.height) / 15000);
      for (let i = 0; i < numParticles; i++) {
        particles.push(createParticle());
      }
    };

    const createParticle = () => {
      return {
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 1.5 + 0.5,
        speedX: (Math.random() - 0.5) * 0.2,
        speedY: (Math.random() - 0.5) * 0.2,
        opacity: Math.random() * 0.5 + 0.1,
        life: 0,
        maxLife: Math.random() * 200 + 100,
      };
    };

    const draw = () => {
      ctx.fillStyle = '#050B14'; // Dark deep blue void color
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw subtle radial gradient in the center
      const gradient = ctx.createRadialGradient(
        canvas.width / 2,
        canvas.height / 2,
        0,
        canvas.width / 2,
        canvas.height / 2,
        canvas.width / 2
      );
      gradient.addColorStop(0, 'rgba(18, 38, 70, 0.4)'); // Inner glow
      gradient.addColorStop(1, 'rgba(5, 11, 20, 1)'); // Outer dark

      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw particles (stars/dust)
      particles.forEach((p, index) => {
        p.x += p.speedX;
        p.y += p.speedY;
        p.life++;

        // Fade in and out based on life
        let currentOpacity = p.opacity;
        if (p.life < 50) {
          currentOpacity = p.opacity * (p.life / 50);
        } else if (p.life > p.maxLife - 50) {
          currentOpacity = p.opacity * ((p.maxLife - p.life) / 50);
        }

        if (p.life >= p.maxLife) {
          particles[index] = createParticle();
        }

        // Wrap around screen
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(180, 210, 255, ${currentOpacity})`;
        ctx.fill();
      });

      animationFrameId = requestAnimationFrame(draw);
    };

    window.addEventListener('resize', resize);
    resize();
    draw();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none fixed inset-0 z-[-1]"
      style={{ background: '#050B14' }}
    />
  );
}
