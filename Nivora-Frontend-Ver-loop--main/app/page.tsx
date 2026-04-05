import { HeroSectionVideo } from '@/components/landing/hero-section-video';
import { EnhancedCompanyLogosSection } from '@/components/landing/enhanced-company-logos-section';
import { TabbedShowcaseSection } from '@/components/landing/tabbed-showcase-section';
import { DeveloperPlatformSection } from '@/components/landing/developer-platform-section';
import { HowItWorksSection } from '@/components/landing/how-it-works-section';
import { CTASection, Footer } from '@/components/landing/cta-section';

export default function Page() {
  return (
    <>
      <main className="min-h-screen bg-black">
        <HeroSectionVideo />
        <EnhancedCompanyLogosSection />
        <TabbedShowcaseSection />
        <DeveloperPlatformSection />
        <HowItWorksSection />
        <CTASection />
      </main>
      <Footer />
    </>
  );
}
