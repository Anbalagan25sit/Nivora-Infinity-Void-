import { HeroSectionVideo } from '@/components/landing/hero-section-video';
import { FeaturesSection } from '@/components/landing/features-section';
import { ArchitectureSection } from '@/components/landing/architecture-section';
import { ComparisonSection } from '@/components/landing/comparison-section';

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-background">
      <HeroSectionVideo />
      <FeaturesSection />
      <ArchitectureSection />
      <ComparisonSection />
    </main>
  );
}
