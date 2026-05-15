# Nivora Landing Page

A stunning, production-grade landing page for Nivora AI agent, inspired by LiveKit's dark aesthetic.

## 🎨 Design Features

### Hero Section

- Full viewport height with animated gradient orb background
- Large, bold headline with gradient text effects
- Floating terminal code snippet with blinking cursor
- Technology badge (LiveKit + n8n + AWS Nova Pro)
- Primary CTA: "Try Live Demo" → links to `/playground`
- Secondary CTA: "View on GitHub"
- Scroll indicator with smooth animation
- CSS-only noise texture overlay for depth

### Features Section

- 6 feature cards in responsive grid (3x2)
- Each card features:
  - Gradient icon background
  - Animated entrance on scroll (Intersection Observer)
  - Hover glow effects
  - Dark card design (#111111) with subtle borders
- Features:
  1. Voice First (sub-200ms latency)
  2. n8n Workflows (400+ integrations)
  3. Screen Intelligence (AWS Nova Pro)
  4. Works Offline (Ollama local LLMs)
  5. Persistent Memory
  6. Plugin Ecosystem

### Architecture Diagram Section

- SVG-based animated flow diagram
- Color-coded nodes:
  - Blue: User Voice → LiveKit
  - Purple: Agent Core, AWS Nova Pro, Ollama
  - Green: n8n Workflows
  - Orange: Actions
- Animated connection lines using stroke-dashoffset
- Auto-loops every 4 seconds
- 3 statistics cards below:
  - <200ms voice latency
  - 400+ n8n integrations
  - 100% local by default

### Comparison Table Section

- Competitive comparison with Claude Cowork and Comet Agent
- 10 feature rows with checkmarks/crosses
- Nivora column highlighted with purple border
- "Most Powerful" badge
- Scroll-triggered animations for each row
- Nivora shows all features, competitors show limitations

### CTA & Footer

- Final call-to-action section
- Download button + GitHub link
- Social media icons (GitHub, Twitter, Discord)
- Footer with links and branding

### Navigation

- Fixed top navigation with backdrop blur
- Logo, nav links, and CTAs
- "Star on GitHub" button
- Smooth scroll animations

## 🎭 Aesthetic Choices

### Color Palette

- Background: #0a0a0a (deep black)
- Cards: #111111 (dark gray)
- Borders: #222222 with hover states
- Primary gradient: Purple (#a855f7) to Cyan (#06b6d4)
- Accent colors: Blue, Green, Orange for feature differentiation

### Typography

- Uses existing font stack (Public Sans / Commit Mono)
- Large, bold headlines (6xl-8xl)
- Gradient text effects for emphasis
- Monospace for code snippets

### Animations

- Framer Motion for scroll-triggered reveals
- CSS keyframe animations:
  - `pulse-slow`: Gradient orb pulsing
  - `float`: Vertical floating motion
  - `blink`: Terminal cursor
  - `scroll`: Scroll indicator
- Staggered delays for sequential reveals
- Intersection Observer for performance

### Effects

- Animated gradient orbs (purple/cyan/pink)
- Noise texture overlay (SVG filter)
- Glow effects on hover
- Backdrop blur on glass-morphism elements
- Box shadows with colored glow

## 📁 File Structure

```
components/landing/
├── navigation.tsx          # Top nav bar
├── hero-section.tsx        # Main hero with gradient orb
├── features-section.tsx    # 6 feature cards
├── architecture-section.tsx # Animated flow diagram
├── comparison-section.tsx   # Comparison table
└── cta-section.tsx         # Final CTA + Footer

app/
├── page.tsx               # Landing page (/)
└── playground/page.tsx    # Voice playground (/playground)

styles/
└── globals.css           # Custom animations added
```

## 🚀 Usage

### Main Landing Page

Visit `http://localhost:3000` to see the full landing page.

### Voice Playground

The original voice assistant playground is accessible at `http://localhost:3000/playground`.

### Navigation Flow

- Hero CTA "Try Live Demo" → `/playground`
- All GitHub links → External (would need real URLs)

## 🎯 Design Philosophy

This landing page avoids generic AI aesthetics by:

1. **Bold Color Choices**: Purple-to-cyan gradients instead of overused purple-on-white
2. **Distinctive Typography**: Large, impactful headlines with gradient clipping
3. **Motion with Purpose**: Every animation serves a narrative purpose
4. **Depth & Atmosphere**: Layered glows, noise textures, and blur effects
5. **Dark-First Design**: Embraces dark mode as primary aesthetic
6. **Technical Details**: Shows actual code, architecture, and metrics
7. **Competitive Positioning**: Clear, honest comparison table

## 🛠️ Technical Stack

- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS 4
- **Animations**: Framer Motion (motion/react)
- **Icons**: Lucide React
- **Performance**:
  - Intersection Observer for scroll animations
  - CSS-only effects where possible
  - Optimized gradient rendering
  - No heavy dependencies

## 📱 Responsive Design

- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px)
- Grid layouts collapse to single column on mobile
- Navigation adapts with hidden links on small screens
- Touch-friendly button sizes

## 🎨 Customization

### Change Colors

Edit gradient definitions in each component:

```tsx
from-purple-600 to-purple-500  // Primary gradient
from-cyan-400 to-blue-400      // Accent gradient
```

### Adjust Animations

Modify timing in `styles/globals.css`:

```css
.animate-pulse-slow {
  animation: pulse-slow 4s ease-in-out infinite;
}
```

### Update Content

All text content is in the component files - no external CMS needed.

## 🔥 Key Differentiators

1. **Animated SVG Architecture**: Hand-coded flow diagram with color-coded nodes
2. **Floating Code Snippet**: Terminal-style code block with blinking cursor
3. **Scroll-Triggered Reveals**: Professional staggered animation entrance
4. **Competitive Comparison**: Honest, clear feature comparison table
5. **Dark Aesthetic**: Inspired by LiveKit but with unique purple-cyan identity

---

Built with Claude Code and exceptional attention to detail. 🚀
