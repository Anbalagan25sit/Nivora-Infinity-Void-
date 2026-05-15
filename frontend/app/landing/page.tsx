import { ArchitectureSection } from '@/components/landing/architecture-section';
import { ComparisonSection } from '@/components/landing/comparison-section';
import { FeaturesSection } from '@/components/landing/features-section';
import { HeroSectionVideo } from '@/components/landing/hero-section-video';

export default function LandingPage() {
  return (
    <main className="bg-background min-h-screen">
      <HeroSectionVideo />
      <FeaturesSection />
      <ArchitectureSection />
      <ComparisonSection />
    </main>
  );
}
